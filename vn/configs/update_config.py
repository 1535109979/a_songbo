# 打开包含配置的Python文件
with open('config.py', 'r') as file:
    content = file.read()

# 执行配置文件中的Python代码
exec(content)


DemoConfigs.strategy_config['avail_down'] = 200000
new_content = repr(DemoConfigs)

# 修改配置值
# strategy_config['avail_down'] = 200000
#
# # 将修改后的配置内容转换为字符串
# new_content = repr(strategy_config)
#
# # 将新的配置内容写回文件
with open('config_.py', 'w') as file:
    file.write(new_content)

