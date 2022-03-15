class MasterSlaveDBRouter(object):
    def db_for_read(self, model, **hints):
        # 返回slave配置 --> 指向从mysql
        return 'slave'

    def db_for_write(self, model, **hints):
        # 返回default配置 --> 指向主mysql
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True


__all__ = [
    "MasterSlaveDBRouter"
]
