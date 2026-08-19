from land_monitor.main import main


def test_main_smoke(capsys):
    main()
    output = capsys.readouterr().out
    assert "Land Monitor smoke test: OK" in output
