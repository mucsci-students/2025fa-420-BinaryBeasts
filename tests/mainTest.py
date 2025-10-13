import models.main_model as main_model
import controllers.main_controller as main_controller
import views.cli.main_view as main_view

def main():
    model = main_model.main_model()
    controller = main_controller.main_controller(model)
    controller.load_config("example.json")
    controller.generate_schedules(10)

main()