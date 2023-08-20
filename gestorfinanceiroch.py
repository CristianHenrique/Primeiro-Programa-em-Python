import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QCalendarWidget, QInputDialog, QAction, QFileDialog
from PyQt5.QtGui import QColor, QPainter, QPixmap, QFont, QFontMetrics, QPalette, QIcon
from PyQt5.QtCore import Qt, QDate, QTimer, QPoint, QEvent

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QFile

import matplotlib.pyplot as plt
import pandas as pd
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from datetime import datetime
import os


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
        salario_update_button = QPushButton("Atualizar")
        salario_update_button.clicked.connect(self.update_salario)
        salario_layout.addWidget(salario_update_button)
        salario_layout.setAlignment(Qt.AlignLeft)

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

        dividas_layout = QHBoxLayout()
        dividas_layout.addWidget(dividas_label)
        dividas_layout.addWidget(self.dividas_nome_edit)
        dividas_layout.addWidget(self.dividas_valor_edit)
        dividas_layout.addWidget(dividas_button)
        dividas_remove_button = QPushButton("Remover")
        dividas_layout.addWidget(dividas_remove_button)
        dividas_remove_button.clicked.connect(self.remove_divida)
        dividas_layout.setAlignment(Qt.AlignLeft)


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
        rendas_remove_button = QPushButton("Remover")
        rendas_layout.addWidget(rendas_remove_button)
        rendas_remove_button.clicked.connect(self.remove_renda)

        evolucao_button = QPushButton("Ver Evolução Financeira")
        evolucao_button.clicked.connect(self.show_evolucao_dialog)
        main_layout.addWidget(evolucao_button)

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
        sobra = self.salario_total + sum(renda['valor'] for renda in self.rendas_fora) - self.dividas_total
        return sobra

    def create_chart(self):
        # Cria o gráfico de pizza com base nos dados financeiros
        if self.dividas_total == 0 and not self.rendas_fora:
            return

        labels = ['Dívidas Total', 'Rendas por Fora']
        sizes = [self.dividas_total, sum(renda['valor'] for renda in self.rendas_fora)]
        colors = ['red', 'green']

        # Remover valores inválidos (NaN) e seus respectivos rótulos
        sizes = [size for size in sizes if not np.isnan(size)]
        labels = [label for size, label in zip(sizes, labels) if not np.isnan(size)]
        colors = colors[:len(labels)]

        # Verificar se há dados para exibir no gráfico após a remoção dos valores inválidos
        if not sizes or not labels:
            return

        # Plotando o gráfico
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        # Salvando o gráfico em um arquivo temporário
        temp_chart = 'chart.png'
        plt.savefig(temp_chart, transparent=True)  # Usar 'transparent=True' para remover o fundo branco
        plt.close()

        # Carregando o arquivo do gráfico na interface
        chart_pixmap = QPixmap(temp_chart)
        self.chart_label.setPixmap(chart_pixmap)

        # Atualizando a caixa de informações
        info_text = "Salário Total:\n"
        info_text += f"Total: R${self.salario_total:.2f}\n"
        info_text += "\nDívidas:\n"
        info_text += f"Total: R${self.dividas_total:.2f}\n"
        for divida in self.dividas:
            info_text += f"{divida['nome']}: R${divida['valor']:.2f}\n"
        info_text += "\nRendas por Fora:\n"
        for renda in self.rendas_fora:
            info_text += f"{renda['nome']}: R${renda['valor']:.2f}\n"
        # Adicionando o valor que sobra do salário
        sobra = self.calcular_sobra_salario()
        info_text += f"\nSobra do Salário: R${sobra:.2f}\n"

        self.info_box.setPlainText(info_text)

    
    def show_evolucao_dialog(self):
             evolucao_dialog = EvolucaoFinanceiraDialog(self, self.get_evolucao_data())
            
             evolucao_dialog.exec_()
    
    def get_evolucao_data(self):
         evolucao_data = []
         
         sobra_acumulada = 0
         for mes in range(1, 13):
              sobra_acumulada += self.calcular_sobra_mes(mes)
              evolucao_data.append((mes, sobra_acumulada))
         
         return evolucao_data


    def calcular_sobra_mes(self, mes):
              rendas_mes = [renda['valor'] for renda in self.rendas_fora if renda.get('mes') == mes]
              dividas_mes = [divida['valor'] for divida in self.dividas if divida.get('mes') == mes]

              sobra_mes = self.salario_total + sum(rendas_mes) - sum(dividas_mes)
              return sobra_mes
    
    def open_monthly_chart(self):
         meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

         sobras_meses = [self.calcular_sobra_mes(mes) for mes in meses]

         plt.figure(figsize=(8, 6))
         plt.plot(meses, sobras_meses, marker='o')
         plt.title('Evolução Financeira Mensal')
         plt.xlabel('Mês')
         plt.ylabel('Sobra Financeira')
         plt.xticks(rotation=45)
         plt.tight_layout()

         plt.show()



    def add_salario(self):
        # Adiciona o valor do salário total e atualiza o gráfico
        salario_text = self.salario_edit.text()
        if salario_text:
            self.salario_total = float(salario_text)
            self.create_chart()
            self.clear_input_fields()

    def update_salario(self):
                novo_salario_text, ok = QInputDialog.getText(self, "Atualizar Salário Total", "Digite o novo valor do salário total:")
                if ok and novo_salario_text:
                    novo_salario = float(novo_salario_text)
                    self.salario_total = novo_salario
                    self.create_chart()
                    self.clear_input_fields()

    def add_divida(self):
        # Adiciona uma dívida à lista e atualiza o gráfico
        nome = self.dividas_nome_edit.text()
        valor_text = self.dividas_valor_edit.text()
        mes = self.calendar.selectedDate().toString("yyyy-MM")
        if valor_text and valor_text.isdigit():
            valor = float(valor_text)
            self.dividas_total += valor
            self.dividas.append({'nome': nome, 'valor': valor, 'mes': mes})
            self.create_chart()
            self.info_text.append(f"Dívida: {nome} - R${valor:.2f}")
            self.clear_input_fields()
        else:
            self.info_text.append("Valor inválido para a dívida.")

    def remove_divida(self):
                nome_divida = self.dividas_nome_edit.text()
                if nome_divida:
                    for divida in self.dividas:
                        if divida['nome'] == nome_divida:
                            self.dividas_total -= divida['valor']
                            self.dividas.remove(divida)
                            self.create_chart()
                            self.info_text.append(f"Dívida removida: {nome_divida}")
                            self.clear_input_fields()
                            break
                        else:
                            self.info_text.append(f"Dívida não encontrada: {nome_divida}")
                else:
                         self.info_text.append("Digite o nome da dívida a ser removida.")       
    def add_renda(self):
        # Adiciona uma outra renda do salário à lista e atualiza o gráfico
        nome = self.rendas_nome_edit.text()
        valor_text = self.rendas_valor_edit.text()
        mes = self.calendar.selectedDate().toString("yyyy-MM")
        if valor_text and valor_text.isdigit():
            valor = float(valor_text)
            self.rendas_fora.append({'nome': nome, 'valor': valor, 'mes': mes})
            self.create_chart()
            self.info_text.append(f"Renda por Fora: {nome} - R${valor:.2f}")
            self.clear_input_fields()
        else:
            self.info_text.append("Valor inválido para a renda por fora.")
            
    def remove_renda(self):
        nome_renda = self.rendas_nome_edit.text()
        if nome_renda:
            for renda in self.rendas_fora:
                if renda['nome'] == nome_renda:
                    self.rendas_fora.remove(renda)
                    self.create_chart()
                    self.info_text.append(f"Renda por fora removida: {nome_renda}")
                    self.clear_input_fields()
                    break
                else:
                    self.info_text.append(f"Renda por fora não encontrada: {nome_renda}")
            else:
                 self.info_text.append("Digite o nome da renda por fora a ser removida.")       

    def update_text_animation(self):
        # Atualiza a animação do widget de lembretes
        if self.animating_text:
            self.animating_text = self.animating_text[1:] + self.animating_text[0]
            self.lembretes_bar.setPlainText(self.animating_text)

    def show_selected_date(self):
        # Exibe a data selecionada no calendário e adiciona um lembrete
        selected_date = self.calendar.selectedDate()
        lembrete, ok = QInputDialog.getText(self, "Adicionar Lembrete", "Digite o lembrete:")
        if ok and lembrete:
            self.info_text.append(f"Lembrete: {selected_date.toString()} - {lembrete}")
            self.lembretes.append(f"Lembrete: {selected_date.toString()} - {lembrete}")

            # Adiciona o lembrete ao widget de lembretes e inicia a animação
            if not self.animating_text:
                self.animating_text = "Lembrete: {0} - {1}".format(selected_date.toString(), lembrete)
                self.lembretes_bar.setPlainText(self.animating_text)
                self.text_animation_timer.start(self.text_speed)
            else:
                self.animating_text += "\nLembrete: {0} - {1}".format(selected_date.toString(), lembrete)

    def paintEvent(self, event):
        # Desenha o gráfico na interface
        painter = QPainter(self)

        # Posição do gráfico
        chart_pixmap = self.chart_label.pixmap()
        if chart_pixmap:
            chart_geometry = self.chart_label.geometry()
            new_chart_geometry = chart_geometry.translated(400, 100)
            painter.drawPixmap(new_chart_geometry, chart_pixmap)

    def clear_input_fields(self):
        # Limpa os campos de entrada de dados
        self.salario_edit.clear()
        self.dividas_nome_edit.clear()
        self.dividas_valor_edit.clear()
        self.rendas_nome_edit.clear()
        self.rendas_valor_edit.clear()

    def load_data(self):
        # Carrega os dados a partir de um arquivo de texto
        file_path, _ = QFileDialog.getOpenFileName(self, "Carregar Dados", "", "Arquivos de Texto (*.txt);;Todos os Arquivos (*)")
        if not file_path:
            return

        with open(file_path, 'r') as file:
            lines = file.readlines()

        self.salario_total = float(lines[0].split(':')[1].strip().split('R$')[1])
        self.dividas_total = float(lines[1].split(':')[1].strip().split('R$')[1])

        self.dividas = []
        index = 3
        while lines[index] != '\n':
            divida_info = lines[index].split(':')
            nome = divida_info[0].strip()
            valor = float(divida_info[1].strip().split('R$')[1])
            self.dividas.append({'nome': nome, 'valor': valor})
            index += 1

        self.rendas_fora = []
        index += 2
        while lines[index] != '\n':
            renda_info = lines[index].split(':')
            nome = renda_info[0].strip()
            valor = float(renda_info[1].strip().split('R$')[1])
            self.rendas_fora.append({'nome': nome, 'valor': valor})
            index += 1

        self.lembretes = []
        index += 2
        while index < len(lines):
            lembrete = lines[index].strip()
            self.lembretes.append(lembrete)
            index += 1

        self.create_chart()
        self.load_lembretes()

    def load_lembretes(self):
        # Carrega os lembretes para o widget de lembretes e inicia a animação
        if self.lembretes:
            self.animating_text = "\n".join(self.lembretes)
            self.lembretes_bar.setPlainText(self.animating_text)
            self.text_animation_timer.start(self.text_speed)

    def save_data(self):
        # Salva os dados em um arquivo de texto
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Dados", "", "Arquivos de Texto (*.txt);;Todos os Arquivos (*)")
        if not file_path:
            return

        with open(file_path, 'w') as file:
            file.write(f"Salário Total: R${self.salario_total:.2f}\n")
            file.write(f"Dívidas Total: R${self.dividas_total:.2f}\n")
            file.write("Dívidas:\n")
            for divida in self.dividas:
                file.write(f"{divida['nome']}: R${divida['valor']:.2f}\n")
            file.write("\nRendas por Fora:\n")
            for renda in self.rendas_fora:
                file.write(f"{renda['nome']}: R${renda['valor']:.2f}\n")
            sobra = self.calcular_sobra_salario()
            file.write(f"\nSobra do Salário: R${sobra:.2f}\n")

            file.write("\nLembretes:\n")
            for lembrete in self.lembretes:
                file.write(f"{lembrete}\n")

    def reset_data(self):
        # Função para recomeçar o cálculo e limpar todos os dados
        self.salario_total = 0
        self.dividas_total = 0
        self.rendas_fora = []
        self.dividas = []
        self.lembretes = []
        self.create_chart()
        self.info_box.clear()
        self.lembretes_bar.clear()

        # Limpa o gráfico de pizza
        empty_pixmap = QPixmap()
        self.chart_label.setPixmap(empty_pixmap)

        # Limpa a barra de animações
        self.animating_text = ""
        self.lembretes_bar.setPlainText("")

    def closeEvent(self, event):
        # Remove o arquivo temporário do gráfico e fecha o aplicativo
        temp_chart = 'chart.png'
        QFile.remove(temp_chart)
        event.accept()

class EvolucaoFinanceiraDialog(QDialog):
            def __init__(self, organizer_app, data):
                
                super().__init__()

                self.setWindowTitle("Evolução Financeira")
                self.setGeometry(100, 100, 800, 600)

                self.organizer_app = organizer_app
                self.data = data

                self.create_layout()

            def create_layout(self):
                    layout = QVBoxLayout()

                    label = QLabel("Gráfico de Evolução Financeira")
                    label.setAlignment(Qt.AlignCenter)
                    layout.addWidget(label)

                    button = QPushButton("Gerar Gráfico")
                    button.clicked.connect(self.generate_chart)
                    layout.addWidget(button)

                    self.setLayout(layout)

            def generate_chart(self):
                df = pd.DataFrame(self.get_evolucao_data(), columns=['Mês', 'Ganhos', 'Gastos', 'Sobra'])

                current_month = datetime.now().strftime('%B')
                df = df[df['Mês'] >= current_month]

                plt.figure(figsize=(8, 6))
                plt.plot(df['Mês'], df['Ganhos'], label='Ganhos', marker='o')
                plt.plot(df['Mês'], df['Gastos'], label='Gastos', marker='o')
                plt.plot(df['Mês'], df['Sobra'], label='Sobra', marker='o')

                plt.title('Evolução Financeira Mensal')
                plt.xlabel('Mês')
                plt.ylabel('Valor')
                plt.xticks(df['Mês'], rotation=45)

                plt.legend()
                plt.tight_layout()

                plt.show()

            def recuperar_dados_mensais(self, nome_mes):
                 arquivo_path = f'{nome_mes}.txt'

                 if os.path.exists(arquivo_path):
                    with open(arquivo_path, 'r') as arquivo:
                         linhas = arquivo.readlines()
                         ganhos = float(linhas[0].split(':')[1].strip().split('R$')[1])
                         gastos = float(linhas[1].split(':')[1].strip().split('R$')[1])
                         sobra = float(linhas[2].split(':')[1].strip().split('R$')[1])

                         return {'ganhos': ganhos, 'gastos': gastos, 'sobra': sobra}
                 else:
                          return {'ganhos': 0, 'gastos': 0, 'sobra': 0}
                 


            
            def get_evolucao_data(self):
                     evolucao_data = []
                     current_month = datetime.now().month
                     
                     meses_ordenados = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]



                     for mes in meses_ordenados[current_month - 1:]:
                          dados_mensais = self.recuperar_dados_mensais(mes)

                          ganhos = dados_mensais['ganhos']
                          gastos = dados_mensais['gastos']
                          sobra_acumulada = dados_mensais['sobra']

                          evolucao_data.append((mes, ganhos, gastos, sobra_acumulada))

                     return evolucao_data    




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_icon = QIcon('C:\\Users\\csdoq\\OneDrive\\Área de Trabalho\\gestorfinaceiroch\\iconch.ico')  
    app.setWindowIcon(app_icon)
    organizer = OrganizerApp()
    organizer.show()
    sys.exit(app.exec_())
