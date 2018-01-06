import pyglet
import esper


FPS = 60
RESOLUTION = 720, 480


##################################
#  Define some Components:
##################################
class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class PhysicsBody:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Renderable(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, batch):
        super().__init__(img=img, x=x, y=y, batch=batch)


################################
#  Define some Processors:
################################
class MovementProcessor(esper.Processor):
    def __init__(self, minx, maxx, miny, maxy):
        super().__init__(fps=15)
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self, dt):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (vel, body) in self.world.get_components(Velocity, PhysicsBody):
            # Update the Renderable Component's position by it's Velocity:
            # An example of keeping the sprite inside screen boundaries. Basically,
            # adjust the position back inside screen boundaries if it is outside:
            # new_x = max(self.minx, body.x + vel.x)
            # new_y = max(self.miny, body.y + vel.y)
            # new_x = min(self.maxx - body.width, new_x)
            # new_y = min(self.maxy - body.height, new_y)
            # body.x = new_x
            # body.y = new_y

            body.x += vel.x * self.ms_per_update
            body.y += vel.y * self.ms_per_update


class RenderProcessor(esper.Processor):
    def __init__(self):
        super().__init__(fps=60)

    def process(self, dt):
        for ent, (rend, body) in self.world.get_components(Renderable, PhysicsBody):
            rend.position = body.x, body.y


###############################################
#  Initialize pyglet window and graphics batch:
###############################################
window = pyglet.window.Window(width=RESOLUTION[0],
                              height=RESOLUTION[1],
                              caption="Esper pyglet example",
                              vsync=False)
batch = pyglet.graphics.Batch()

# Initialize Esper world, and create a "player" Entity with a few Components:
world = esper.FlexWorld()

player = world.create_entity()
world.add_component(player, Velocity(x=0, y=0))
player_image = pyglet.image.SolidColorImagePattern((255, 0, 0, 255)).create_image(64, 64)
world.add_component(player, Renderable(img=player_image, x=100, y=100, batch=batch))
world.add_component(player, PhysicsBody(x=100, y=100, width=64, height=64))

# Another motionless Entity:
enemy = world.create_entity()
enemy_image = pyglet.image.SolidColorImagePattern((0, 0, 255, 255)).create_image(64, 64)
world.add_component(enemy, Renderable(img=enemy_image, x=400, y=250, batch=batch))
world.add_component(enemy, PhysicsBody(x=400, y=250, width=64, height=64))

# Assign some Processor instances to the World to be processed:
world.add_processor(MovementProcessor(minx=0, miny=0, maxx=RESOLUTION[0], maxy=RESOLUTION[1]))
world.add_processor(RenderProcessor())


################################################
#  Set up pyglet events for input and rendering:
################################################
@window.event
def on_key_press(key, mod):
    if key == pyglet.window.key.RIGHT:
        world.component_for_entity(player, Velocity).x = 300
    if key == pyglet.window.key.LEFT:
        world.component_for_entity(player, Velocity).x = -300
    if key == pyglet.window.key.UP:
        world.component_for_entity(player, Velocity).y = 300
    if key == pyglet.window.key.DOWN:
        world.component_for_entity(player, Velocity).y = -300


@window.event
def on_key_release(key, mod):
    if key in (pyglet.window.key.RIGHT, pyglet.window.key.LEFT):
        world.component_for_entity(player, Velocity).x = 0
    if key in (pyglet.window.key.UP, pyglet.window.key.DOWN):
        world.component_for_entity(player, Velocity).y = 0


@window.event
def on_draw():
    # Clear the window:
    window.clear()
    # Draw the batch of Renderables:
    batch.draw()


####################################################
#  Schedule a World update and start the pyglet app:
####################################################
if __name__ == "__main__":
    # NOTE!  schedule_interval will automatically pass a "delta time" argument
    #        to world.process, so you must make sure that your Processor classes
    #        account for this. See the example Processors above.
    pyglet.clock.schedule_interval(world.process, 1/60)
    pyglet.app.run()
