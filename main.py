import pygame
import sys
import random
import textwrap
import time
import json
# Constantes para la pantalla
WIDTH = 900
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 250)
GREEN = (50, 200, 50)
RED = (250, 50, 50)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)


# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quiz de GESTION DE LAS ORGANIZAIONES INDUSTRIALES")
font = pygame.font.SysFont("arial", 12)
clock = pygame.time.Clock()

# --- DATOS DEL QUIZ ---
# Las preguntas se cargan directamente desde la estructura JSON

with open('preguntas.json', 'r', encoding='utf-8') as archivo:
    preguntas_respuestas = json.load(archivo)


# --- VARIABLES DE ESTADO ---
estado = "menu"
preguntas_activas = []
respuestas_usuario = []
respondidas = []
indice_actual = 0
mostrar_feedback = False
color_feedback = WHITE
mensaje_feedback = ""
feedback_time = 0
mostrar_respuesta_desarrollar = False
mostrar_respuesta_mc = False

# --- FUNCIONES DE DIBUJO ---
def draw_button(text, x, y, w, h, color, text_color=WHITE, border_color=None, border_width=10):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    if border_color:
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)
    
    # --- Renderizado de texto con wrap ---
    lines = textwrap.wrap(text, width=40)  # Ajusta el número para controlar el largo de línea
    line_height = font.get_height()
    total_height = len(lines) * line_height + (len(lines)-1)*5  # espacio entre líneas

    y_offset = y + (h - total_height) // 2  # centra verticalmente
    for line in lines:
        txt = font.render(line, True, text_color)
        screen.blit(txt, (x + (w - txt.get_width()) // 2, y_offset))
        y_offset += line_height + 2  # 5 px de separación entre líneas

    return rect


def render_wrapped_text(text, x, y, max_width, line_spacing=5, color=BLACK):
    lines = textwrap.wrap(text, width=70)
    for i, line in enumerate(lines):
        rendered_line = font.render(line, True, color)
        screen.blit(rendered_line, (x, y + i * (rendered_line.get_height() + line_spacing)))
    return y + len(lines) * (font.get_height() + line_spacing)

def mostrar_resultado_final():
    screen.fill(WHITE)
    correctas = 0
    for i, pregunta in enumerate(preguntas_activas):
        # Para preguntas de opción múltiple, se compara la respuesta del usuario
        if pregunta["tipo"] == "multiple_choice" and respuestas_usuario[i] == pregunta["respuesta_correcta"]:
            correctas += 1
        # Para preguntas de desarrollo, se verifica si el usuario marcó "Acerté"
        elif pregunta["tipo"] == "desarrollar" and respuestas_usuario[i] == "Acerté":
            correctas += 1
    
    total = len(preguntas_activas)
    incorrectas = total - correctas
    porcentaje = (correctas / total) * 100 if total > 0 else 0
    
    titulo = font.render("📝 Resultado Final", True, BLACK)
    screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 100))
    screen.blit(font.render(f"Correctas: {correctas}", True, GREEN), (250, 180))
    screen.blit(font.render(f"Incorrectas: {incorrectas}", True, RED), (250, 220))
    screen.blit(font.render(f"Porcentaje de aciertos: {porcentaje:.2f}%", True, BLUE), (250, 260))
    pygame.display.flip()
    time.sleep(5)
    pygame.quit()
    sys.exit()

# --- BUCLE PRINCIPAL ---
running = True
while running:
    # Reiniciar los botones en cada ciclo para evitar errores de referencia
    btn_ant = None
    btn_sig = None
    btn_mostrar_respuesta_mc = None
    btn_mostrar_respuesta_desarrollar = None
    btn_acerte = None
    btn_no_acerte = None
    btn_siguiente_desarrollar = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if estado == "menu":
            # ... (Lógica de menú sin cambios)
            screen.fill(WHITE)
            titulo = font.render("📘Quiz de GESTION DE LAS ORGANIZACIONES INDUSTRIALES", True, BLACK)
            screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 100))
            btn_iniciar = draw_button("Iniciar Quiz", 300, 200, 300, 50, BLUE)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_iniciar.collidepoint(event.pos):
                    preguntas_activas = preguntas_respuestas.copy()
                    random.shuffle(preguntas_activas)
                    respuestas_usuario = [None] * len(preguntas_activas)
                    respondidas = [False] * len(preguntas_activas)
                    indice_actual = 0
                    mostrar_feedback = False
                    estado = "quiz"
                    mostrar_respuesta_desarrollar = False
                    mostrar_respuesta_mc = False

        elif estado == "quiz":
            screen.fill(WHITE)
            
            if indice_actual >= len(preguntas_activas):
                mostrar_resultado_final()
            
            pregunta_actual = preguntas_activas[indice_actual]
            tipo_pregunta = pregunta_actual["tipo"]
            
            # Encabezado del quiz
            total_preguntas = len(preguntas_activas)
            aciertos = sum(1 for i, p in enumerate(preguntas_activas) if (p["tipo"] == "multiple_choice" and respuestas_usuario[i] == p.get("respuesta_correcta")) or (p["tipo"] == "desarrollar" and respuestas_usuario[i] == "Acerté"))
            progreso_txt = f"Pregunta {indice_actual + 1} de {total_preguntas}  |  Aciertos: {aciertos}"
            progreso_render = font.render(progreso_txt, True, BLACK)
            screen.blit(progreso_render, (WIDTH // 2 - progreso_render.get_width() // 2, 10))

            # Dibujar la pregunta
            y_pregunta = render_wrapped_text(pregunta_actual["pregunta"], 50, 50, WIDTH - 100)
            
            # Dibuja el botón de "Anterior" si no es la primera pregunta
            if indice_actual > 0:
                btn_ant = draw_button("⬅ Anterior", 150, 500, 150, 40, GRAY)

            # --- Lógica para preguntas de opción múltiple ---
            if tipo_pregunta == "multiple_choice":
                opciones = pregunta_actual["opciones"]
                respuesta_correcta = pregunta_actual["respuesta_correcta"]
                
                opcion_buttons = []
                y_pos = y_pregunta + 30
                for opcion in opciones:
                    color = BLUE
                    border_color = None
                    if respondidas[indice_actual] or mostrar_respuesta_mc:
                        if opcion == respuesta_correcta:
                            border_color = GREEN
                        if respuestas_usuario[indice_actual] == opcion and opcion != respuesta_correcta:
                            color = RED
                    
                    btn = draw_button(opcion, 100, y_pos, 700, 40, color, BLACK if color == WHITE else WHITE, border_color)
                    opcion_buttons.append(btn)
                    y_pos += 60

                if not mostrar_respuesta_mc and not respondidas[indice_actual]:
                    btn_mostrar_respuesta_mc = draw_button("Mostrar Respuesta", 375, 500, 150, 40, YELLOW, BLACK)
                else:
                    btn_sig = draw_button("Siguiente ➡", 500, 500, 150, 40, GRAY)
            
            # --- Lógica para preguntas de desarrollo ---
            elif tipo_pregunta == "desarrollar":
                y_pos = y_pregunta + 30

                if not mostrar_respuesta_desarrollar:
                    btn_mostrar_respuesta_desarrollar = draw_button("Mostrar Respuesta", 375, 500, 150, 40, YELLOW, BLACK)
                else:
                    respuesta_correcta = pregunta_actual["respuesta_correcta"]
                    if isinstance(respuesta_correcta, (list, set)):
                        for r in respuesta_correcta:
                            y_pos = render_wrapped_text(f"• {r}", 50, y_pos, WIDTH - 100)
                    else:
                        y_pos = render_wrapped_text(respuesta_correcta, 50, y_pos, WIDTH - 100)
                    
                    if not respondidas[indice_actual]:
                        btn_acerte = draw_button("Acerté", 200, 500, 150, 40, GREEN, WHITE)
                        btn_no_acerte = draw_button("No Acerté", 550, 500, 150, 40, RED, WHITE)
                    else:
                        btn_siguiente_desarrollar = draw_button("Siguiente ➡", 500, 500, 150, 40, BLUE)

            # --- Manejo de eventos de clic ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Botón "Anterior"
                if btn_ant and btn_ant.collidepoint(event.pos) and indice_actual > 0:
                    indice_actual -= 1
                    mostrar_respuesta_mc = False
                    mostrar_respuesta_desarrollar = False
                
                # Lógica para preguntas de opción múltiple
                if tipo_pregunta == "multiple_choice":
                    if not respondidas[indice_actual] and not mostrar_respuesta_mc:
                        for i, btn in enumerate(opcion_buttons):
                            if btn.collidepoint(event.pos):
                                respuesta_elegida = opciones[i]
                                respuestas_usuario[indice_actual] = respuesta_elegida
                                respondidas[indice_actual] = True
                                
                                if respuesta_elegida == respuesta_correcta:
                                    mensaje_feedback = "✅ ¡Correcto!"
                                    color_feedback = GREEN
                                else:
                                    mensaje_feedback = "❌ Incorrecto."
                                    color_feedback = RED
                                
                                mostrar_feedback = True
                                feedback_time = pygame.time.get_ticks()
                    
                    if btn_mostrar_respuesta_mc and btn_mostrar_respuesta_mc.collidepoint(event.pos):
                        mostrar_respuesta_mc = True
                    
                    if btn_sig and btn_sig.collidepoint(event.pos) and indice_actual < len(preguntas_activas) - 1:
                        indice_actual += 1
                        mostrar_respuesta_mc = False
                        mostrar_respuesta_desarrollar = False
                    elif btn_sig and btn_sig.collidepoint(event.pos) and indice_actual == len(preguntas_activas) - 1:
                        mostrar_resultado_final()
                
                # Lógica para preguntas de desarrollo
                elif tipo_pregunta == "desarrollar":
                    if btn_mostrar_respuesta_desarrollar and btn_mostrar_respuesta_desarrollar.collidepoint(event.pos):
                        mostrar_respuesta_desarrollar = True
                    
                    if not respondidas[indice_actual]:
                        if btn_acerte and btn_acerte.collidepoint(event.pos):
                            respuestas_usuario[indice_actual] = "Acerté"
                            respondidas[indice_actual] = True
                        if btn_no_acerte and btn_no_acerte.collidepoint(event.pos):
                            respuestas_usuario[indice_actual] = "No Acerté"
                            respondidas[indice_actual] = True
                    
                    if btn_siguiente_desarrollar and btn_siguiente_desarrollar.collidepoint(event.pos):
                        indice_actual += 1
                        mostrar_respuesta_desarrollar = False
                        mostrar_respuesta_mc = False

            # Mostrar feedback si corresponde
            if mostrar_feedback and tipo_pregunta == "multiple_choice":
                pygame.draw.rect(screen, color_feedback, pygame.Rect(300, 450, 300, 40), border_radius=6)
                screen.blit(font.render(mensaje_feedback, True, WHITE), (310, 455))
                if pygame.time.get_ticks() - feedback_time > 1500:
                    mostrar_feedback = False
                    indice_actual += 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()