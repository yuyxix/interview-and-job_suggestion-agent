import asyncio
import time

# 异步，即多个任务同时进行
async def task(name, seconds):
    print(f"任务 {name} 开始，需要 {seconds} 秒")
    await asyncio.sleep(seconds)  # 模拟异步等待（不阻塞）
    print(f"任务 {name} 完成")
    return f"结果-{name}"


async def main():
    start = time.time()

    # 创建三个任务，同时出发
    tasks = [
        asyncio.create_task(task("A", 2)),
        asyncio.create_task(task("B", 1)),
        asyncio.create_task(task("C", 3))
    ]

    # 等待所有任务完成
    results = await asyncio.gather(*tasks)

    print(f"所有结果: {results}")
    print(f"总耗时: {time.time() - start:.2f} 秒")


if __name__ == "__main__":
    asyncio.run(main())