from fastapi import APIRouter, Depends

from app.admin.entity import AdminEntity
from app.admin.service import AdminService
from app.common.PermissionUtil import has_roles

admin_router = APIRouter()


@admin_router.get(
    path='/users',
    summary='获取用户列表',
    description='管理员查看所有用户（含角色）',
)
def get_users(user: dict = Depends(has_roles('admin'))):
    return AdminService.list_users()


@admin_router.get(
    path='/profiles',
    summary='查看所有用户画像',
    description='管理员查看所有用户的画像 —— 只读，不能修改',
)
def get_profiles(user: dict = Depends(has_roles('admin'))):
    return AdminService.list_user_profiles()


@admin_router.get(
    path='/profile/{user_id}',
    summary='查看指定用户画像',
    description='管理员查看单个用户的画像 —— 只读，不能修改',
)
def get_profile(user_id: int, user: dict = Depends(has_roles('admin'))):
    return AdminService.get_user_profile(user_id)


@admin_router.get(
    path='/get_user',
    summary='获取用户信息',
    description='通过用户名获取用户信息',
)
def get_user(username: str, user: dict = Depends(has_roles('admin'))):
    return AdminService.get_user(username)


@admin_router.post(
    path='/delete_user/{username}',
    summary='删除用户',
    description='通过用户名删除用户，并清理该用户的记忆数据',
)
def delete_user(username: str, user: dict = Depends(has_roles('admin'))):
    # 防止管理员把自己删了（前端已经禁用按钮，后端再兜一层）
    if username == user.get('username'):
        return {'code': 400, 'msg': '不能删除当前登录账号', 'data': None}
    return AdminService.delete_user(username)


@admin_router.put(
    path='/change_role',
    summary='修改用户角色',
    description='角色只能是 user 或 admin',
)
def change_role(adminEntity: AdminEntity.ChangeRolesEntity,
                user: dict = Depends(has_roles('admin'))):
    # 防止管理员把自己降级后无法再进后台
    if (adminEntity.username == user.get('username')
            and adminEntity.role_name != 'admin'):
        return {'code': 400, 'msg': '不能修改当前登录账号的角色', 'data': None}
    return AdminService.change_role(adminEntity.role_name, adminEntity.username)


# 兼容旧路径：/admin/changeRoles/{role_name}
@admin_router.put(
    path='/changeRoles/{role_name}',
    summary='修改用户角色（旧路径）',
    description='修改用户角色，兼容旧调用',
)
def change_roles_legacy(role_name: str,
                        adminEntity: AdminEntity.ChangeRolesEntity,
                        user: dict = Depends(has_roles('admin'))):
    if (adminEntity.username == user.get('username')
            and role_name != 'admin'):
        return {'code': 400, 'msg': '不能修改当前登录账号的角色', 'data': None}
    return AdminService.change_role(role_name, adminEntity.username)


