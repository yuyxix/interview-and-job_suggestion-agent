import json

from app.admin.dao import AdminDao
from app.ai.agent.multi_agent.memory.manage.memory_manager import get_collection
from app.ai.agent.multi_agent.memory.save.profile_memory import ProfileMemory
from app.common import RedisUtil

VALID_ROLES = ('user', 'admin')


def list_users():
    users = AdminDao.list_users() or []
    return {'code': 200, 'msg': '获取用户列表成功', 'data': users}


def get_user(username):
    user = AdminDao.get_user(username)
    if not user:
        return {'code': 404, 'msg': '用户不存在', 'data': None}
    return {'code': 200, 'msg': '获取用户成功', 'data': user}


def list_user_profiles():
    """管理员查看所有用户画像 —— 只读，不提供修改入口"""
    users = AdminDao.list_users() or []
    data = []
    for user in users:
        data.append({**user, 'profile': _read_profile(user['user_id'])})
    return {'code': 200, 'msg': '获取用户画像成功', 'data': data}


def get_user_profile(user_id):
    user = AdminDao.get_user_by_id(user_id)
    if not user:
        return {'code': 404, 'msg': '用户不存在', 'data': None}
    return {
        'code': 200,
        'msg': '获取用户画像成功',
        'data': {**user, 'profile': _read_profile(user_id)},
    }


def _read_profile(user_id):
    """读单个用户的画像；读失败就当空画像，不影响用户列表展示"""
    try:
        return ProfileMemory(str(user_id)).query() or ''
    except Exception as e:
        print(f'读取用户 {user_id} 画像失败: {type(e).__name__}: {e}')
        return ''


def change_role(role_name, username):
    if role_name not in VALID_ROLES:
        return {'code': 400, 'msg': '角色只能是 user 或 admin', 'data': None}
    if AdminDao.change_roles(role_name, username) == 1:
        return {'code': 200, 'msg': '修改用户角色成功', 'data': None}
    return {'code': 500, 'msg': '修改用户角色失败（用户不存在？）', 'data': None}


def delete_user(username):
    user = AdminDao.delete_user(username)
    if not user:
        return {'code': 404, 'msg': '用户不存在或删除失败', 'data': None}
    # 账号删掉后，把这个用户在各记忆层的残留一起清掉（失败不影响删账号）
    cleanup_user_memory(user['user_id'], username)
    return {
        'code': 200,
        'msg': '删除用户成功',
        'data': {'user_id': user['user_id']},
    }


def cleanup_user_memory(user_id, username):
    """清理某用户在各记忆层的残留

    · Redis：画像、画像轮次、会话轮次、窗口记忆、token、会话记录
    · Chroma：长期记忆
    · PG：摘要 + LangGraph checkpoint
    """
    uid = str(user_id)
    sessions = set()

    # 1) Redis
    try:
        r = RedisUtil.get_redis_con()
        keys = [f'profile:{uid}', f'profile_turn:{uid}', username]

        for pattern in (f'windows_memory:{uid}:*', f'memory_turn:{uid}:*'):
            for key in r.scan_iter(match=pattern):
                keys.append(key)
                parts = key.split(':', 2)
                if len(parts) == 3:
                    sessions.add(parts[2])

        # session 记录里存了 user_id，顺便把该用户的会话和会话锁也带上
        for key in r.scan_iter(match='session*'):
            try:
                raw = r.get(key)
                info = json.loads(raw) if raw else {}
                if str(info.get('user_id')) == uid:
                    sessions.add(key)
                    keys.append(key)
            except Exception:
                pass

        for sid in sessions:
            keys.append(f'session_lock:{sid}')

        if keys:
            r.delete(*keys)
        RedisUtil.close_redis_con(r)
    except Exception as e:
        print(f'清理用户 {uid} Redis 记忆失败: {type(e).__name__}: {e}')

    # 2) Chroma（先取 session_id，后面清 checkpoint 要用）
    try:
        collection = get_collection()
        rs = collection.get(
            where={'user_id': {'$eq': uid}},
            include=['metadatas'],
        )
        for meta in rs.get('metadatas') or []:
            sid = (meta or {}).get('session_id')
            if sid:
                sessions.add(str(sid))
        collection.delete(where={'user_id': {'$eq': uid}})
    except Exception as e:
        print(f'清理用户 {uid} 长期记忆失败: {type(e).__name__}: {e}')

    # 3) PG：摘要 + checkpoint
    try:
        from app.ai.agent.multi_agent.memory.save.summary_memory import pool
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute(
                    'DELETE FROM conversation_summary WHERE user_id=%s',
                    (uid,),
                )
                if sessions:
                    sids = sorted(sessions)
                    cur.execute(
                        'DELETE FROM checkpoint_writes WHERE thread_id = ANY(%s)',
                        (sids,),
                    )
                    cur.execute(
                        'DELETE FROM checkpoint_blobs WHERE thread_id = ANY(%s)',
                        (sids,),
                    )
                    cur.execute(
                        'DELETE FROM checkpoints WHERE thread_id = ANY(%s)',
                        (sids,),
                    )
            con.commit()
    except Exception as e:
        print(f'清理用户 {uid} PG 记忆失败: {type(e).__name__}: {e}')
    