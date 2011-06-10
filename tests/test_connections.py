from dingus import Dingus

from nydus.db import Cluster
from nydus.db.routers import BaseRouter
from nydus.db.backends import BaseConnection

from . import BaseTest, dingus_calls_to_dict

class DummyConnection(BaseConnection):
    def __init__(self, resp='foo', **kwargs):
        self.resp = resp
        super(DummyConnection, self).__init__(**kwargs)

    def foo(self, *args, **kwargs):
        return self.resp

class DummyRouter(BaseRouter):
    def get_db(self, pool, func, key=None, *args, **kwargs):
        # Assume first argument is a key
        if key == 'foo':
            return [1]
        return [0]

class ClusterTest(BaseTest):
    def test_init(self):
        c = Cluster(
            hosts={0: BaseConnection(num=1)},
        )
        self.assertEquals(len(c), 1)
        self.assertTrue(c.redis)
    
    def test_proxy(self):
        c = DummyConnection(num=1, resp='bar')
        p = Cluster(
            hosts={0: c},
        )
        self.assertEquals(p.foo(), 'bar')

    def test_disconnect(self):
        c = Dingus()
        p = Cluster(
            hosts={0: c},
        )
        p.disconnect()
        calls = dingus_calls_to_dict(c.calls)
        self.assertTrue('disconnect' in calls)

    def test_with_router(self):
        c = DummyConnection(num=0, resp='foo')
        c2 = DummyConnection(num=1, resp='bar')

        # test dummy router
        r = DummyRouter()
        p = Cluster(
            hosts={0: c, 1: c2},
            router=r,
        )
        self.assertEquals(p.foo(), 'foo')
        self.assertEquals(p.foo('foo'), 'bar')

        # test default routing behavior
        p = Cluster(
            hosts={0: c, 1: c2},
        )
        self.assertEquals(p.foo(), ['foo', 'bar'])
        self.assertEquals(p.foo('foo'), ['foo', 'bar'])
