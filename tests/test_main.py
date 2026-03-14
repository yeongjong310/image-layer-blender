from merge_image_layer.main import App


def test_app_instantiation():
    app = App()
    assert app.title() == "이미지 합성 프로그램"
    app.destroy()
