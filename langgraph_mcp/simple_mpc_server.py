from mcp.server.fastmcp import FastMCP

mcp = FastMCP("simplemcp", port=5001)


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    读取指定文件的内容
    
    Args:
        file_path (str): 要读取的文件路径，支持相对路径和绝对路径
        
    Returns:
        str: 文件的内容，以字符串形式返回
        
    Raises:
        FileNotFoundError: 当文件不存在时抛出
        PermissionError: 当没有读取权限时抛出
        UnicodeDecodeError: 当文件编码不是UTF-8时抛出
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool()
def write_to_file(file_path: str, content: str) -> str:
    """
    将指定内容写入到文件中
    
    Args:
        file_path (str): 要写入的文件路径，支持相对路径和绝对路径
        content (str): 要写入的内容，会自动将\\n转换为换行符
        
    Returns:
        str: 操作结果信息，"写入成功"表示成功
        
    Raises:
        PermissionError: 当没有写入权限时抛出
        OSError: 当文件路径无效或磁盘空间不足时抛出
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.replace("\\n", "\n"))
    return "写入成功"

@mcp.tool()
def run_terminal_command(command: str) -> str:
    """
    在终端中执行指定的命令
    
    Args:
        command (str): 要执行的终端命令，支持shell命令
        
    Returns:
        str: 命令执行结果，成功时返回"执行成功"，失败时返回错误信息
        
    Note:
        此函数会使用shell=True执行命令，请确保命令来源可信
        对于长时间运行的命令，可能会阻塞执行
    """
    import subprocess
    run_result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return "执行成功" if run_result.returncode == 0 else run_result.stderr

@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Greet a person by name."""
    print(f"roy mcp demo called : greeting({name})")
    return f"Hello, {name}!"

if __name__ == "__main__":
    # 以sse协议暴露服务。 
    mcp.settings.host = "0.0.0.0"
    mcp.run(transport='streamable-http') 
    # 以stdio协议暴露服务。
    # mcp.run(transport='stdio')
 
 