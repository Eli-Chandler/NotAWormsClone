import arcade

class PhysicsEngine:
    def __init__(self, player, walls_list, gravity_constant):
        self.player = player
        self.walls_list = walls_list
        self.gravity_constant = gravity_constant
        self.can_jump_value = False
        self.stair_height = 20

        self.on_ground = False
        self.hit_roof = False

    def check_collision_x(self, delta_time):
        self.player.center_x += self.player.change_x * delta_time
        hit_list = arcade.check_for_collision_with_list(self.player, self.walls_list)
        self.player.center_x -= self.player.change_x * delta_time
        return hit_list

    def check_collision_y(self, delta_time):
        self.player.center_y += self.player.change_y * delta_time
        hit_list = arcade.check_for_collision_with_list(self.player, self.walls_list)
        self.player.center_y -= self.player.change_y * delta_time
        return hit_list

    def check_can_stair(self, hits_x, hits_y, delta_time):
        if hits_x:
            if self.check_on_ground(hits_x, hits_y):
                distance_to_highest = max([hit_x.top for hit_x in hits_x]) - self.player.bottom
                if distance_to_highest + 1 < self.stair_height:
                    # Temporarily move the player up to check for collision
                    self.player.center_y += distance_to_highest + 1
                    new_hits_x = self.check_collision_x(delta_time)
                    self.player.center_y -= (distance_to_highest + 1)
                    if not new_hits_x:
                        # If there is no collision, the player can stair step
                        return distance_to_highest
            return False

    def check_on_ground(self, hits_x, hits_y):
        if self.player.change_y < 0 and hits_y:
            return True
        return False

    def check_hit_roof(self, hits_x, hits_y):
        if self.player.change_y > 0 and hits_y:
            return True
        return False

    def can_jump(self, delta_time):
        self.player.center_y -= 3
        hits = self.check_collision_y(delta_time)
        self.player.center_y += 3
        if hits:
            return True
        return False

    def update(self, delta_time):
        # Apply gravity


        if self.can_jump(delta_time) and self.player.want_to_jump:
            self.player.change_y = self.player.jump_speed

        amount_to_move_x = 0
        amount_to_move_y = 0

        hits_x = self.check_collision_x(delta_time)
        hits_y = self.check_collision_y(delta_time)

        self.on_ground = self.check_on_ground(hits_x, hits_y)
        can_stair = self.check_can_stair(hits_x, hits_y, delta_time)
        self.hit_roof = self.check_hit_roof(hits_x, hits_y)

        if hits_x:
            if can_stair:
                amount_to_move_x = self.player.change_x
                self.player.center_y += can_stair
        else:
            amount_to_move_x += self.player.change_x

        if hits_y:
            if self.on_ground and self.player.change_y > 0:
                amount_to_move_y = self.player.change_y
            if self.hit_roof and self.player.change_y < 0:
                amount_to_move_y = self.player.change_y

        else:
            amount_to_move_y += self.player.change_y

        self.player.center_x += amount_to_move_x * delta_time
        self.player.center_y += amount_to_move_y * delta_time

        if self.hit_roof and self.player.change_y > 0:
            self.player.change_y = 0

        if self.on_ground and self.player.change_y <= 0:
            self.player.change_x = 0
            self.player.change_y = 0
        else:
            self.player.change_x = self.player.change_x * (1 - delta_time)
            self.player.change_y -= self.gravity_constant