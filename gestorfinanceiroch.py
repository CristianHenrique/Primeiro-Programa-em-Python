import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QCalendarWidget, QInputDialog, QAction, QFileDialog, QMessageBox
from PyQt5.QtGui import QColor, QPainter, QPixmap, QFont, QFontMetrics, QPalette, QIcon
from PyQt5.QtCore import Qt, QDate, QTimer, QPoint, QEvent

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QFile

class OrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador Financeiro")
        self.setGeometry(100, 100, 1200, 800)  # Tamanho da janela
        # Variáveis para armazenar os dados financeiros
        self.salario_total = 0
        self.dividas_total = 0
        self.rendas_fora = []
        self.dividas = []
        self.lembretes = []

        # Configuração da interface gráfica
        self.create_layout()
        self.create_chart()

        # Configurações para a animação do widget de lembretes
        self.animating_text = ""
        self.text_animation_timer = QTimer(self)
        self.text_animation_timer.timeout.connect(self.update_text_animation)
        self.text_speed = 170

        # Variáveis para permitir a movimentação do widget de lembretes
        self.dragging = False
        self.offset = QPoint()

        # Configuração do menu
        self.init_menu()

    def init_menu(self):
        # Inicializa o menu da aplicação com as ações de salvar e carregar dados
        save_action = QAction("Salvar Dados", self)
        save_action.triggered.connect(self.save_data)
        self.menuBar().addAction(save_action)

        load_action = QAction("Carregar Dados", self)
        load_action.triggered.connect(self.load_data)
        self.menuBar().addAction(load_action)

        # Ação para excluir dívidas
        delete_divida_action = QAction("Excluir Dívida", self)
        delete_divida_action.triggered.connect(self.show_delete_divida_dialog)
        self.menuBar().addAction(delete_divida_action)

        # Ação para excluir rendas por fora
        delete_renda_action = QAction("Excluir Renda por Fora", self)
        delete_renda_action.triggered.connect(self.show_delete_renda_dialog)
        self.menuBar().addAction(delete_renda_action)

    def create_layout(self):
        # Criação e organização dos widgets da interface gráfica
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        salario_label = QLabel("Salário Total:")
        self.salario_edit = QLineEdit()
        salario_button = QPushButton("Adicionar")
        salario_button.clicked.connect(self.add_salario)

        salario_layout = QHBoxLayout()
        salario_layout.addWidget(salario_label)
        salario_layout.addWidget(self.salario_edit)
        salario_layout.addWidget(salario_button)

        dividas_label = QLabel("Dívidas:")
        self.dividas_nome_edit = QLineEdit()
        self.dividas_valor_edit = QLineEdit()
        dividas_button = QPushButton("Adicionar")
        dividas_button.clicked.connect(self.add_divida)

        dividas_layout = QHBoxLayout()
        dividas_layout.addWidget(dividas_label)
        dividas_layout.addWidget(self.dividas_nome_edit)
        dividas_layout.addWidget(self.dividas_valor_edit)
        dividas_layout.addWidget(dividas_button)

        rendas_label = QLabel("Outras rendas:")
        self.rendas_nome_edit = QLineEdit()
        self.rendas_valor_edit = QLineEdit()
        rendas_button = QPushButton("Adicionar")
        rendas_button.clicked.connect(self.add_renda)

        rendas_layout = QHBoxLayout()
        rendas_layout.addWidget(rendas_label)
        rendas_layout.addWidget(self.rendas_nome_edit)
        rendas_layout.addWidget(self.rendas_valor_edit)
        rendas_layout.addWidget(rendas_button)

        self.calendar = QCalendarWidget()
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.show_selected_date)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)

        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setFixedWidth(400)
        self.chart_label.setFixedHeight(400)

        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)

        self.lembretes_bar = QTextEdit()
        self.lembretes_bar.setReadOnly(True)
        self.lembretes_bar.setFixedWidth(300)
        self.lembretes_bar.setFixedHeight(125)
        palette = self.lembretes_bar.palette()
        palette.setColor(QPalette.Base, QColor(0, 0, 0, 165))  # Fundo preto 65% transparente
        palette.setColor(QPalette.Text, Qt.white)  # Texto branco
        self.lembretes_bar.setPalette(palette)
        font = QFont("Arial", 12)  # Tamanho de fonte do lembrete
        self.lembretes_bar.setFont(font)

        main_layout.addLayout(salario_layout)
        main_layout.addLayout(dividas_layout)
        main_layout.addLayout(rendas_layout)

        info_chart_layout = QHBoxLayout()
        info_chart_layout.addWidget(self.info_box)
        info_chart_layout.addWidget(self.chart_label)
        main_layout.addLayout(info_chart_layout)

        lembretes_layout = QHBoxLayout()
        lembretes_layout.addWidget(self.lembretes_bar)
        lembretes_layout.addStretch(1)
        lembretes_layout.setAlignment(Qt.AlignRight)
        main_layout.addLayout(lembretes_layout)

        main_layout.addWidget(self.calendar)

        # Botão "Recomeçar"
        recomecar_button = QPushButton("Recomeçar")
        recomecar_button.clicked.connect(self.reset_data)
        main_layout.addWidget(recomecar_button)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Habilita o rastreamento do mouse e instala o filtro de eventos para permitir a movimentação do widget de lembretes
        self.lembretes_bar.setMouseTracking(True)
        self.lembretes_bar.installEventFilter(self)

    def eventFilter(self, source, event):
        # Filtra os eventos do widget de lembretes para permitir a movimentação
        if source is self.lembretes_bar and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.dragging = True
                self.offset = event.pos()
                return True
        elif event.type() == QEvent.MouseMove and self.dragging:
            if event.buttons() & Qt.LeftButton:
                self.lembretes_bar.move(self.mapToGlobal(event.pos() - self.offset))
                return True
            else:
                self.dragging = False
        return super().eventFilter(source, event)

    def calcular_sobra_salario(self):
        # Calcula o valor que sobra do salário após deduzir as dívidas e adicionar as rendas por fora
        return self.salario_total - self.dividas_total + sum(self.rendas_fora)

    def add_salario(self):
        # Adiciona o salário total digitado ao valor já existente
        try:
            salario = float(self.salario_edit.text())
            self.salario_total += salario
            self.salario_edit.clear()
            self.update_info()
        except ValueError:
            self.show_message_box("Erro", "Por favor, digite um valor numérico válido para o salário.")

    def add_divida(self):
        # Adiciona uma dívida com nome e valor digitados à lista de dívidas
        nome = self.dividas_nome_edit.text()
        valor_text = self.dividas_valor_edit.text()
        try:
            valor = float(valor_text)
            self.dividas.append({"nome": nome, "valor": valor})
            self.dividas_total += valor
            self.dividas_nome_edit.clear()
            self.dividas_valor_edit.clear()
            self.update_info()
        except ValueError:
            self.show_message_box("Erro", "Por favor, digite um valor numérico válido para a dívida.")

    def add_renda(self):
        # Adiciona uma renda por fora com nome e valor digitados à lista de rendas por fora
        nome = self.rendas_nome_edit.text()
        valor_text = self.rendas_valor_edit.text()
        try:
            valor = float(valor_text)
            self.rendas_fora.append(valor)
            self.rendas_nome_edit.clear()
            self.rendas_valor_edit.clear()
            self.update_info()
        except ValueError:
            self.show_message_box("Erro", "Por favor, digite um valor numérico válido para a renda.")

    def update_info(self):
        # Atualiza o texto exibido na caixa de informações
        sobra_salario = self.calcular_sobra_salario()
        info_text = f"Salário Total: R${self.salario_total:.2f}\n"
        info_text += f"Dívidas Totais: R${self.dividas_total:.2f}\n"
        info_text += f"Rendas por Fora: R${sum(self.rendas_fora):.2f}\n"
        info_text += f"Sobra do Salário: R${sobra_salario:.2f}"
        self.info_text.setPlainText(info_text)

        # Atualiza o gráfico
        self.update_chart()

    def create_chart(self):
        # Cria um gráfico de pizza inicialmente vazio
        self.chart_label.setPixmap(QPixmap())

    def update_chart(self):
        # Atualiza o gráfico de pizza com os dados atuais
        if self.salario_total == 0:
            # Não há dados para exibir, mostra um gráfico vazio
            self.create_chart()
            return

        # Configurações do gráfico
        labels = ['Dívidas', 'Rendas por Fora', 'Sobra do Salário']
        sizes = [self.dividas_total, sum(self.rendas_fora), self.calcular_sobra_salario()]
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        explode = (0.1, 0, 0)  # Destacar a primeira fatia (dívidas)

        # Criação e exibição do gráfico
        plt.cla()  # Limpa o gráfico anterior
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')  # Assegura que o gráfico seja desenhado como um círculo.
        plt.savefig('chart.png')  # Salva o gráfico como uma imagem temporária
        self.chart_label.setPixmap(QPixmap('chart.png'))  # Exibe a imagem no QLabel do gráfico

    def show_selected_date(self):
        # Exibe a informação do dia selecionado no calendário
        selected_date = self.calendar.selectedDate().toString(Qt.ISODate)
        lembrete = self.get_lembrete_for_date(selected_date)
        self.info_box.setPlainText(lembrete)

    def get_lembrete_for_date(self, date):
        # Obtém o lembrete para uma data específica
        for lembrete_date, text in self.lembretes:
            if lembrete_date == date:
                return text
        return ""

    def update_text_animation(self):
        # Atualiza a animação de rolagem do texto no widget de lembretes
        if len(self.animating_text) == 0:
            return

        current_text = self.lembretes_bar.toPlainText()
        if not current_text:
            self.lembretes_bar.setPlainText(self.animating_text[0])
            self.animating_text = self.animating_text[1:]
        else:
            self.lembretes_bar.setPlainText(current_text[1:] + self.animating_text[0])
            self.animating_text = self.animating_text[1:]

    def show_message_box(self, title, text):
        # Exibe uma caixa de mensagem com o título e texto fornecidos
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.exec_()

    def show_delete_divida_dialog(self):
        # Exibe uma caixa de diálogo para excluir uma dívida
        divida_names = [divida["nome"] for divida in self.dividas]
        item, ok = QInputDialog.getItem(self, "Excluir Dívida", "Selecione a dívida a ser excluída:", divida_names, editable=False)
        if ok and item:
            index = divida_names.index(item)
            divida_valor = self.dividas[index]["valor"]
            self.dividas_total -= divida_valor
            del self.dividas[index]
            self.update_info()

    def show_delete_renda_dialog(self):
        # Exibe uma caixa de diálogo para excluir uma renda por fora
        renda_names = [f"Renda {i+1}" for i in range(len(self.rendas_fora))]
        item, ok = QInputDialog.getItem(self, "Excluir Renda por Fora", "Selecione a renda por fora a ser excluída:", renda_names, editable=False)
        if ok and item:
            index = renda_names.index(item)
            renda_valor = self.rendas_fora[index]
            del self.rendas_fora[index]
            self.update_info()

    def save_data(self):
        # Salva os dados financeiros em um arquivo de texto
        file_name, _ = QFileDialog.getSaveFileName(self, "Salvar Dados", "", "Text Files (*.txt);;All Files (*)")
        if not file_name:
            return

        with open(file_name, "w") as file:
            file.write(f"Salário Total: {self.salario_total:.2f}\n")
            file.write(f"Dívidas:\n")
            for divida in self.dividas:
                file.write(f"{divida['nome']}: {divida['valor']:.2f}\n")
            file.write(f"Rendas por Fora:\n")
            for renda in self.rendas_fora:
                file.write(f"{renda:.2f}\n")

        self.show_message_box("Sucesso", "Os dados foram salvos com sucesso!")

    def load_data(self):
        # Carrega os dados financeiros de um arquivo de texto
        file_name, _ = QFileDialog.getOpenFileName(self, "Carregar Dados", "", "Text Files (*.txt);;All Files (*)")
        if not file_name:
            return

        with open(file_name, "r") as file:
            lines = file.readlines()

        self.salario_total = 0
        self.dividas_total = 0
        self.rendas_fora = []
        self.dividas = []
        for line in lines:
            if line.startswith("Salário Total:"):
                self.salario_total = float(line.split(":")[1].strip())
            elif line == "Dívidas:\n":
                is_dividas = True
            elif line == "Rendas por Fora:\n":
                is_dividas = False
            elif is_dividas:
                nome, valor = line.split(":")
                self.dividas.append({"nome": nome.strip(), "valor": float(valor.strip())})
                self.dividas_total += float(valor.strip())
            else:
                self.rendas_fora.append(float(line.strip()))

        self.update_info()
        self.show_message_box("Sucesso", "Os dados foram carregados com sucesso!")

    def reset_data(self):
        # Reseta os dados financeiros e reinicia o programa
        self.salario_total = 0
        self.dividas_total = 0
        self.rendas_fora = []
        self.dividas = []
        self.lembretes = []
        self.info_text.setPlainText("")
        self.lembretes_bar.setPlainText("")
        self.create_chart()

        # Fecha o programa e inicia uma nova instância
        self.close()
        new_instance = OrganizerApp()
        new_instance.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrganizerApp()
    window.show()
    sys.exit(app.exec_())
