import pytest
from datetime import datetime
from models import check_dep, Departments, db


def create_dep(p_dep_name):
    dt = datetime.now()
    dep_cr = Departments(dt_add=dt, dep_name=p_dep_name, dt_upd=dt)
    db.session.add(dep_cr)
    db.session.commit()


@pytest.mark.parametrize('dt1, dt2', [("test_dep1", "test_dep2")])
def create_dep(dt1, dt2):
    create_dep(dt1)
    create_dep(dt2)
    res1 = check_dep(1, dt1)
    res2 = check_dep(1, dt2)
    assert res1 is None
    assert res2 is None

