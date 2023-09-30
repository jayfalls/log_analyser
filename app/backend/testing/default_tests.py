import asyncio
import inspect
import time


# SPEED
async def test_async_function_speed(function_to_time, *args, **kwargs) -> str:
    # Check if the function is asynchronous
    if not inspect.iscoroutinefunction(function_to_time):
        return "Not a asyncronous function"
    
    start_time = time.time()

    # Run the coroutine and await its completion
    result = await function_to_time(*args, **kwargs)
        
    end_time = time.time()
    return f"Elapsed time: {end_time - start_time}"


def test_function_speed(function_to_time, *args, **kwargs) -> str:
    if inspect.iscoroutinefunction(function_to_time):
        return "Not a syncronous function"

    start_time = time.time()
    
    # If it's a synchronous function, run it directly
    result = function_to_time(*args, **kwargs)
    print(result)

    end_time = time.time()
    return f"Elapsed time: {end_time - start_time}"