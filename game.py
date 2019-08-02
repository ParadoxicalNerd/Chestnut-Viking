import arcade
import os
import random

WINDOW_HEIGHT = 1024 * 4 // 5
WINDOW_WIDTH = 1024
MARGIN = 100

MOVEMENT_SPEED = 2
MOVEMENT_CHANGE = 1.05
GRAVITY_CHANGE = -1.2
GRAVITY = 0.2
LASER_SPEED = 4
LASER_DELAY = 2

SPRITE_SCALING = 0.2
CLOUD_SCALING = 0.6
LASER_SCALING = 1

MAP_HEIGHT = 5


def get_map():
    map_file = open("map.csv")
    map_array = []
    for line in map_file:
        line = line.strip()
        map_row = line.split(",")
        for index, item in enumerate(map_row):
            map_row[index] = int(item)
        map_array.append(map_row)
    return map_array


class myGame(arcade.Window):
    def __init__(self, height, width):
        super().__init__(
            width, height, "30 Second Dash: Prison Break", fullscreen=False
        )
        self.tile_sheet = get_map()

        arcade.set_background_color(arcade.color.BLACK_OLIVE)
        self.lower_platform_list = None
        self.upper_platform_list = None
        self.common_platform_list = None
        self.player_sprite = None
        # self.laser_list = None
        self.pause_physics_engine = None

        self.view_left = None
        self.view_bottom = None

        self.raw_score = 0

    def setup(self):
        self.lower_platform_list = arcade.SpriteList()
        self.upper_platform_list = arcade.SpriteList()
        self.common_platform_list = arcade.SpriteList()

        # self.laser_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite("Character1.png", SPRITE_SCALING)
        self.player_sprite.center_x = 366 // 2
        self.player_sprite.center_y = 500
        self.player_sprite.append_texture(
            arcade.load_texture("Character2.png", scale=SPRITE_SCALING)
        )

        # for i in range(366 // 2, 366 * 15, 366 // 2 + 50):
        #     bottom_cloud = arcade.Sprite("Bottom Cloud.png", CLOUD_SCALING)
        #     bottom_cloud.center_x = i
        #     bottom_cloud.center_y = 80
        #     self.lower_platform_list.append(bottom_cloud)

        for row in range(len(self.tile_sheet)):
            for column in range(len(self.tile_sheet[row])):
                item = self.tile_sheet[row][column]
                if item == 1:
                    cloud = arcade.Sprite(
                        "Top Cloud.png", random.gauss(CLOUD_SCALING, 0.05)
                    )
                elif item == 0:
                    cloud = arcade.Sprite(
                        "Bottom Cloud.png", random.gauss(CLOUD_SCALING, 0.05)
                    )

                if item == 0 or item == 1:
                    cloud.left = column * CLOUD_SCALING * 355 + 100
                    cloud.top = (MAP_HEIGHT - row) * CLOUD_SCALING * 166 + 400
                    self.common_platform_list.append(cloud)

                if item == 0:
                    self.lower_platform_list.append(cloud)
                elif item == 1:
                    self.upper_platform_list.append(cloud)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, self.common_platform_list, GRAVITY
        )

        self.pause_physics_engine = False

        self.view_left = 0
        self.view_bottom = self.player_sprite.bottom - 500
        self.symbol = None
        self.i = 0
        # self._i = 0

        self.GAME_OVER = False
        self.health = 100
        self._ = 0

    def on_key_release(self, symbol, modifiers):
        self.pause_physics_engine = True

        if symbol == arcade.key.UP:
            self.player_sprite.center_y -= 5
            collisions = arcade.check_for_collision_with_list(
                self.player_sprite, self.lower_platform_list
            )
            if len(collisions) > 0:
                self.physics_engine.gravity_constant = (
                    self.physics_engine.gravity_constant * GRAVITY_CHANGE
                )

                self.player_sprite.set_texture(1)

            self.player_sprite.center_y += 5

        if symbol == arcade.key.DOWN:
            self.player_sprite.center_y += 5
            collisions = arcade.check_for_collision_with_list(
                self.player_sprite, self.upper_platform_list
            )
            if len(collisions) > 0:
                self.physics_engine.gravity_constant = (
                    self.physics_engine.gravity_constant * GRAVITY_CHANGE
                )

                self.player_sprite.set_texture(0)

            self.player_sprite.center_y -= 5

        self.pause_physics_engine = False

    def score_board(self):

        global MOVEMENT_SPEED

        arcade.draw_text(
            f"Raw Score: {self.raw_score}    Gravity: {self.physics_engine.gravity_constant:.2f}    Health: {self.health}    Speed: {MOVEMENT_SPEED:.2f}",
            self.view_left + 100,
            self.view_bottom + 50,
            arcade.color.WHITE,
            20,
        )

    def on_draw(self):
        arcade.start_render()
        self.common_platform_list.draw()
        self.player_sprite.draw()
        # self.laser_list.draw()

        self.score_board()

        if self.GAME_OVER or self._ == 1:
            arcade.draw_text(
                "Game Over",
                WINDOW_WIDTH // 2 + self.view_left,
                WINDOW_HEIGHT - 500 + self.view_bottom,
                arcade.color.WHITE,
                font_size=40,
                align="center",
                anchor_x="center",
                anchor_y="center",
                font_name="calibri",
            )

    def update(self, delta_time):
        global MOVEMENT_SPEED
        # global LASER_SPEED
        self.sprite_touching()

        if not self.GAME_OVER:

            self.view_left += MOVEMENT_SPEED
            self.view_bottom = self.player_sprite.bottom - 200
            arcade.set_viewport(
                self.view_left,
                self.view_left + WINDOW_WIDTH,
                self.view_bottom,
                self.view_bottom + WINDOW_HEIGHT,
            )

            if self.view_bottom <= -200 or self.player_sprite.top >= 1000:
                self.GAME_OVER = True

            self.player_sprite.center_x += MOVEMENT_SPEED

            if self.i == 19:
                # LASER_SPEED += MOVEMENT_SPEED * (MOVEMENT_CHANGE - 1.001)
                MOVEMENT_SPEED *= MOVEMENT_CHANGE

            # if self._i == 100:
            #     self.create_laser()
            #     self._i = 0
            # else:
            #     self._i += 1

            self.last_y = self.player_sprite.center_y
            # self.laser_list.update()

            if self.pause_physics_engine == False:
                self.physics_engine.update()

        else:  # In case the game is over
            self.player_sprite.center_y = self.last_y
            self.pause_physics_engine = True
            if self._ == 0:
                self._ = 1

    def sprite_touching(self):

        closest_top_cloud, _ = arcade.get_closest_sprite(
            self.player_sprite, self.upper_platform_list
        )
        closest_bottom_cloud, _ = arcade.get_closest_sprite(
            self.player_sprite, self.lower_platform_list
        )

        if (int(closest_top_cloud.top) == int(self.player_sprite.bottom)) or (
            int(closest_bottom_cloud.bottom) == int(self.player_sprite.top)
        ):
            self.pause_physics_engine = True
            self.GAME_OVER = True

        if self.i == 20 and not self.GAME_OVER:
            self.i = 0
            if (int(closest_top_cloud.bottom) == int(self.player_sprite.top)) or (
                int(closest_bottom_cloud.top) == int(self.player_sprite.bottom)
            ):
                self.raw_score += 1
            else:
                self.health -= 1
        else:
            self.i += 1

    # def create_laser(self):
    #     laser = arcade.Sprite("laser.png", LASER_SCALING)
    #     laser.right = self.view_left

    #     if len(self.laser_list) > 0:
    #         laser.center_y = self.laser_list[-1].center_y
    #         laser.center_y += (
    #             self.player_sprite.center_y - self.laser_list[-1].center_y
    #         ) // LASER_DELAY
    #     else:
    #         laser.center_y = WINDOW_HEIGHT // 2

    #     laser.change_x = LASER_SPEED

    #     self.laser_list.append(copy.deepcopy(laser))


def main():
    game = myGame(WINDOW_HEIGHT, WINDOW_WIDTH)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)
    main()
