from skill_radar.dedupe import normalizar_url, uid_desde_url


def test_normalizar_url_limpia_ruido():
    assert (
        normalizar_url("https://WWW.GitHub.com/a/b/?utm_source=x#readme")
        == "https://github.com/a/b"
    )


def test_repos_de_github_comparten_uid():
    uid1, url1 = uid_desde_url("https://github.com/Foo/Bar/")
    uid2, url2 = uid_desde_url("https://www.github.com/foo/bar?ref=awesome")
    assert uid1 == uid2 == "github:foo/bar"
    assert url1 == url2 == "https://github.com/foo/bar"


def test_urls_web_tienen_uid_estable():
    uid1, _ = uid_desde_url("https://example.com/herramienta/")
    uid2, _ = uid_desde_url("https://example.com/herramienta")
    assert uid1 == uid2
    assert uid1.startswith("web:")


def test_github_con_ruta_no_es_repo_raiz():
    uid, _ = uid_desde_url("https://github.com/foo/bar/tree/main")
    assert uid.startswith("web:")
