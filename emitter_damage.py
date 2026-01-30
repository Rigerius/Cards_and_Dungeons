import arcade
import random
import math


class DamageParticle:
    """Класс для одной частицы урона"""

    def __init__(self, x, y, damage_value, is_critical=False):
        self.x = x
        self.y = y
        self.damage_value = str(damage_value)
        self.life = 1.5  # Время жизни в секундах
        self.max_life = self.life
        self.dy = 50  # Начальная скорость вверх
        self.gravity = -100  # Гравитация

        # Цвета в зависимости от типа урона
        if is_critical:
            self.color = arcade.color.GOLD
            self.size = 26
        else:
            self.color = arcade.color.RED
            self.size = 22

        # Для эффекта "дрожания"
        self.shake_offset_x = random.uniform(-2, 2)
        self.shake_offset_y = random.uniform(-2, 2)

    def update(self, delta_time):
        """Обновление позиции частицы"""
        self.life -= delta_time

        if self.life > 0:
            # Применяем гравитацию
            self.dy += self.gravity * delta_time
            self.y += self.dy * delta_time

            # Медленное движение вверх и в стороны
            self.x += random.uniform(-10, 10) * delta_time

            # Эффект дрожания
            self.shake_offset_x = random.uniform(-2, 2) * (self.life / self.max_life)
            self.shake_offset_y = random.uniform(-2, 2) * (self.life / self.max_life)

            return True
        return False  # Частица умерла

    def draw(self):
        """Отрисовка частицы урона"""
        if self.life > 0:
            # Прозрачность зависит от оставшегося времени жизни
            alpha = int(255 * (self.life / self.max_life))

            # Смещение для дрожания
            draw_x = self.x + self.shake_offset_x
            draw_y = self.y + self.shake_offset_y

            # Рисуем текст урона с эффектом
            arcade.draw_text(
                self.damage_value,
                draw_x, draw_y,
                (self.color[0], self.color[1], self.color[2], alpha),
                self.size,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )


class DamageEmitter:
    """Эмиттер для отображения урона"""

    def __init__(self):
        self.particles = []

    def add_damage(self, x, y, damage_value, is_critical=False):
        """Добавляет частицу урона"""
        particle = DamageParticle(x, y, damage_value, is_critical)
        self.particles.append(particle)

    def update(self, delta_time):
        """Обновляет все частицы"""
        # Удаляем умершие частицы
        self.particles = [p for p in self.particles if p.update(delta_time)]

    def draw(self):
        """Рисует все частицы урона"""
        for particle in self.particles:
            particle.draw()

    def clear(self):
        """Очищает все частицы"""
        self.particles.clear()