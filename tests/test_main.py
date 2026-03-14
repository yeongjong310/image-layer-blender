from merge_image_layer.main import main


def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello from merge-image-layer!\n"
