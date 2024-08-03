import flet as ft
import os

from flet import (UserControl,
                  TextField,
                  InputBorder,
                  Page,
                  ControlEvent)
import json
from time import sleep
import plotly.graph_objects as go

import flet as ft
from flet.plotly_chart import PlotlyChart
from datetime import datetime


class TextEditor(UserControl):
   # new *
    def __init__(self) -> None:
        super().__init__()# инициализация пользовательского интерфейса
        self.textfield = TextField(multiline=True,
                                   autofocus=True,
                                   border=InputBorder.NONE,
                                   min_lines=40,
                                   on_change=self.save_text,
                                   cursor_color='yellow' )# однострочная, ,входная граница , ,сохранение содержимого
    #new *
    def save_text(self, e: ControlEvent) -> None:#сохранение
        with open('note.txt', mode='w', encoding='utf-8') as f:
            f.write(self.textfield.value) #сохранение файла в текстовое поле

    #new *
    def read_text(self) -> str | None: #вернет строку или ничего
        try:# блок
            with open('save.txt', 'r') as f:
                return f.read()
        except   FileNotFoundError: #ошибка
            self.textfield.hint_text = 'Welcome to the text editor' #иначе

    #new *
    def build(self) -> TextField:
            self.textfield.value = self.read_text()#назначение точки для чтения
            return self.textfield
    

class Task(ft.UserControl):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def build(self):
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self)

    def delete_clicked(self, e):
        self.task_delete(self)


class TodoApp(ft.UserControl):
    def build(self):
        self.new_task = ft.TextField(
            hint_text="What needs to be done?", on_submit=self.add_clicked, expand=True
        )
        self.tasks = ft.Column()
        self.active_tasks = ft.Column()  # Добавлен новый контейнер для активных задач
        self.completed_tasks = ft.Column()  # Добавлен новый контейнер для завершенных задач

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="all"), ft.Tab(text="active"), ft.Tab(text="completed")],
        )

        self.items_left = ft.Text("0 items left")

        # application's root control (i.e. "view") containing all other controls
        return ft.Column(
            width=600,
            controls=[
                ft.Row(
                    [ft.Text(value="Todo", style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(
                            icon=ft.icons.ADD, on_click=self.add_clicked
                        ),
                    ],
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.active_tasks,  # Отображение активных задач
                        self.completed_tasks,  # Отображение завершенных задач
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                ft.OutlinedButton(
                                    text="Clear completed", on_click=self.clear_clicked
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    def add_clicked(self, e):
        if self.new_task.value:
            with open(file='notes.txt', mode="a+", encoding="utf-8") as file:
                file.write(f'''Дата: {datetime.today()} | {self.new_task.value}\n''')
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            self.active_tasks.controls.append(task)  # Добавление новой задачи в список активных
            self.new_task.value = ""
            self.new_task.focus()
            self.update_async()

    def task_status_change(self, task):
        if task.completed:
            self.active_tasks.controls.remove(task)
            self.completed_tasks.controls.append(task)
        else:
            self.completed_tasks.controls.remove(task)
            self.active_tasks.controls.append(task)
        self.update_async()

    def task_delete(self, task):
        if task in self.active_tasks.controls:
            self.active_tasks.controls.remove(task)
        else:
            self.completed_tasks.controls.remove(task)
        self.update_async()

    def tabs_changed(self, e):
        self.update_async()

    def clear_clicked(self, e):
        for task in self.completed_tasks.controls[:]:
            self.task_delete(task)

    def update_async(self):
        status = self.filter.tabs[self.filter.selected_index].text
        self.active_tasks.visible = status == "all" or status == "active"
        self.completed_tasks.visible = status == "all" or status == "completed"
        count = len(self.active_tasks.controls)
        self.items_left.value = f"{count} active item(s) left"
        super().update()


class Money(ft.UserControl):
    def build(self):
        self.catego = ft.Column()
        self.int = ft.Column()
        self.notes = ft.Column()

        # Выпадающий список
        self.dropdown = ft.Dropdown(
            label='Выберите категорию',
            width=500,
            options=[
                ft.dropdown.Option("Еда"),
                ft.dropdown.Option("Одежда"),
                ft.dropdown.Option("Услуги"),
                ft.dropdown.Option("Отдых"),
                ft.dropdown.Option("Проживание"),
                ft.dropdown.Option("Транспорт"),
                ft.dropdown.Option("Образование"),
            ],
        )
        # Поле ввода 
        self.notes_textarea = ft.TextField(width=367,
                                    label="Напишите заметку",
                                    value="", 
                                    multiline=False,
                                    min_lines=1,
                                    max_lines=2,
                                    on_submit=self.add_clicked
                                    )
        # диаграмма
        # self.chart = ft.PieChart(
        #     sections=[
        #         ft.PieChartSection(
        #             value=0,
        #             color=ft.colors.BLUE,
        #         ),
        #         ft.PieChartSection(
        #             value=0,
        #             color=ft.colors.YELLOW,
        #         ),
        #         ft.PieChartSection(
        #             value=45,
        #             color=ft.colors.PINK,
        #         ),
        #         ft.PieChartSection(
        #             value=10,
        #             color=ft.colors.GREEN,
        #         ),
        #         ft.PieChartSection(
        #             value=0,
        #             color=ft.colors.BLACK,
        #         ),
        #         ft.PieChartSection(
        #             value=0,
        #             color=ft.colors.CYAN,
        #         ),
        #         ft.PieChartSection(
        #             value=0,
        #             color=ft.colors.BROWN,
        #         ),
        #     ],
        #     sections_space=1,
        #     center_space_radius=0,
        #     on_chart_event=self.on_chart_event,
        #     expand=True,
        #     width=150,
        #     height=150,
        # )
        
        self.chart = PlotlyChart(expand=True, visible=False)
        self.chart_container = ft.Container(
            content=self.chart,
            alignment=ft.alignment.center,
  
        )

        self.add_button = ft.FloatingActionButton("Добавить", width=120, on_click=self.add_clicked)
        self.update_button = ft.FloatingActionButton("Обновить", width=120, on_click=self.update_clicked)

        self.input_field = ft.TextField(width=335, label='Введите сумму затрат', value="0")
        self.products = ft.Column()  # Создаем список задач

        return ft.Column(
    [
        ft.Row([
            ft.Container(
                content=self.dropdown,
                margin=ft.margin.only(top=50)
            )
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([self.input_field], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([self.notes_textarea, self.add_button, self.update_button], alignment=ft.MainAxisAlignment.CENTER),
        self.chart_container,
        ft.Row(controls=[self.catego, self.int, self.products], alignment=ft.MainAxisAlignment.CENTER),
    ]
)
    def update_clicked(self, e):
        # Загрузка JSON из файла
        with open('money.json', encoding='utf-8') as file:
            data = json.load(file)

        # Получаем список ключей из JSON
        keys = list(data.keys())
        labels = []
        values = []

        # Проходим по всем ключам и соответствующим им значениям
        for key, value in zip(keys, data.values()):
            # Находим индекс текущего ключа в списке ключей
            index = keys.index(key)

            # Проверяем, что текущее значение - словарь и содержит поле 'price'
            if isinstance(value, dict) and 'price' in value:
                # Заменяем значение в соответствующем элементе диаграммы
                labels.append(key)
                values.append(value['price'])
                # self.chart.sections[index].title = f'''{key}: {value['price']}'''
                # self.chart.sections[index].value = value['price']
                
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        self.chart.figure = fig

        # Обновляем диаграмму
        self.chart.visible = True
        self.chart.update()
        self.page.update()
        
    def on_chart_event(self, e: ft.PieChartEvent):
        # Загрузка JSON из файла
        with open('money.json', encoding='utf-8') as file:
            data = json.load(file)

        # Получаем список ключей из JSON
        keys = list(data.keys())

        # Проходим по всем ключам и соответствующим им значениям
        for key, value in zip(keys, data.values()):
            # Находим индекс текущего ключа в списке ключей
            index = keys.index(key)

            # Проверяем, что текущее значение - словарь и содержит поле 'price'
            if isinstance(value, dict) and 'price' in value:
                # Заменяем значение в соответствующем элементе диаграммы
                self.chart.sections[index].title = f'''{key}: {value['price']}'''
                self.chart.sections[index].value = value['price']
                
        normal_border = ft.BorderSide(0, ft.colors.with_opacity(0, ft.colors.WHITE))
        hovered_border = ft.BorderSide(6, ft.colors.WHITE)
        for idx, section in enumerate(self.chart.sections):
            
            section.border_side = (
                hovered_border if idx == e.section_index else normal_border
            )
        self.chart.update()

    def update_json(self, item_name, price, notes):
        """
        Функция обновляет цену и описание для указанного элемента в JSON-файле.

        :param item_name: Имя элемента, для которого нужно обновить цену и описание.
        :param price: Цена элемента в виде числа.
        :param notes: Описание элемента в виде текста.
        """
        # Чтение JSON-файла
        with open('money.json', encoding='utf-8') as file:
            data = json.load(file)
        # Обновляем цену и описание для элемента
        data[item_name]["price"] = price
        data[item_name]["notes"] = notes

        # Сохраняем обновленные данные обратно в файл
        with open('money.json', mode='w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def add_clicked(self, e):
        if self.notes_textarea.value and self.input_field and self.dropdown:
            self.update_json(item_name=self.dropdown.value, price=int(self.input_field.value), notes=self.notes_textarea.value.strip())

            note = ft.Text(self.notes_textarea.value, size=20)
            inp_field = ft.Text(self.input_field.value, size=20)
            dropdown = ft.Text(self.dropdown.value, size=20)
            self.catego.controls.append(dropdown)
            self.int.controls.append(inp_field)
            self.products.controls.append(note)

            self.dropdown.value = ""
            self.input_field.value = "0"
            self.notes_textarea.value = ""
            self.notes_textarea.focus()
            self.update()
class Book:
    def __init__(self, title, image_path):
        self.title = title
        self.image_path = image_path
        
class BookshelfApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.books = []
        self.book_containers = []
        self.file_picker = ft.FilePicker(on_result=self.file_picker_result)
        self.title_field = ft.TextField(label="Название учебника")
        self.upload_button = ft.ElevatedButton("Загрузить учебник", on_click=self.pick_files)
        self.bookshelf = ft.Row(wrap=True, spacing=10, run_spacing=10)

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Учебные полки", size=24),
                ft.Row([self.title_field, self.upload_button]),
                self.bookshelf
            ]),
            padding=20,
            bgcolor=ft.colors.BROWN_100
        )

    def pick_files(self, _):
        self.file_picker.pick_files()

    def file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.upload_book(e.files[0])

    def upload_book(self, file):
        if len(self.books) >= 6:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Максимальное количество учебников достигнуто!")))
            return

        if file and self.title_field.value:
            new_book = Book(self.title_field.value, file.path)
            self.books.append(new_book)
            self.add_book_to_shelf(new_book)
            self.title_field.value = ""
            self.update()

    def add_book_to_shelf(self, book):
        book_container = ft.Container(
            content=ft.Column([
                ft.Image(src=book.image_path, width=100, height=150, fit=ft.ImageFit.COVER),
                ft.Text(book.title, size=12),
                ft.ElevatedButton("Читать", on_click=lambda _: os.startfile(filepath='english_grammar.pdf')),
                ft.ElevatedButton("Удалить", on_click=lambda _: self.remove_book(book_container))
            ]),
            padding=10,
            bgcolor=ft.colors.WHITE,
            border_radius=10
        )
        self.book_containers.append(book_container)
        self.bookshelf.controls.append(book_container)
        self.update()

    def remove_book(self, book_container):
        self.bookshelf.controls.remove(book_container)
        self.book_containers.remove(book_container)
        self.update()

def main(page: ft.Page):
    def change_screen(e):
        page.clean()
        if page.navigation_bar.selected_index == 0:
            page.add(Money())
            page.title = "Money"
        elif page.navigation_bar.selected_index == 1:
            page.add(TodoApp())
            page.title = "ToDo App"
            page.scroll = ft.ScrollMode.ADAPTIVE
        elif page.navigation_bar.selected_index == 2:
            page.add(TextEditor())
            page.title = 'Text editor'
            page.scroll = True
        elif page.navigation_bar.selected_index == 3:
            bookshelf_app = BookshelfApp()
            page.overlay.append(bookshelf_app.file_picker)
            page.add(bookshelf_app)
            page.title = 'Книжные полки'
            page.scroll = ft.ScrollMode.ADAPTIVE
    
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.MONEY, label="Money"),
            ft.NavigationDestination(icon=ft.icons.NOTES, label="Notes"),
            ft.NavigationDestination(icon=ft.icons.NOTE, label="Note"),
            ft.NavigationDestination(icon=ft.icons.BOOK, label="Books"),
        ],
        on_change=change_screen
    )

    page.add(Money())
    page.title = "My App"
    
    page.scroll = 'HIDDEN'
    page.adaptive = True

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER


if __name__ == '__main__':
    ft.app(target=main)