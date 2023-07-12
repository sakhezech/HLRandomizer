from hlr.requirements import Req


def test_constants():

    assert Req.ZERO == Req(
        keys=0,
        lasers=0,
        n_modules=0,
        e_modules=0,
        w_modules=0,
        s_modules=0,
        n_pylons=0,
        e_pylons=0,
        w_pylons=0,
        s_pylons=0,
        dash=0,
        sword=0,
    )
    assert Req.FULL == Req(
        keys=16,
        lasers=2,
        n_modules=8,
        e_modules=8,
        w_modules=8,
        s_modules=8,
        n_pylons=0,
        e_pylons=0,
        w_pylons=0,
        s_pylons=0,
        dash=1,
        sword=1,
    )


def test_is_satisfied():
    req_both = Req(dash=1, sword=1)
    req_sword = Req(sword=1)
    req_dash = Req(dash=1)
    req_low_keys = Req(keys=2)
    req_high_keys = Req(keys=10)

    assert req_sword.is_satisfied_by(req_both)
    assert req_dash.is_satisfied_by(req_both)
    assert req_low_keys.is_satisfied_by(req_high_keys)
    assert not req_both.is_satisfied_by(req_dash)
    assert not req_both.is_satisfied_by(req_sword)


def test_any_satisfied():
    req_low_keys = Req(keys=2)
    req_high_keys = Req(keys=10)
    req_low_mods = Req(n_modules=2)
    req_high_mods = Req(n_modules=8)

    assert Req.any_satisfied_by([req_low_keys, req_high_mods], req_high_keys)
    assert Req.any_satisfied_by([req_high_keys, req_low_mods], req_high_mods)
    assert Req.any_satisfied_by([req_high_keys, req_high_mods], req_high_keys)
    assert Req.any_satisfied_by([req_high_keys, req_high_mods], req_high_mods)
    assert not Req.any_satisfied_by(
        [req_high_keys, req_high_mods], req_low_mods
    )
    assert not Req.any_satisfied_by(
        [req_high_keys, req_high_mods], req_low_keys
    )
