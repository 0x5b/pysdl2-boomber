import time
import sdl2.ext

RESOURCES = sdl2.ext.Resources(__file__, "boomber", "resources")

sdl2.ext.init()

window = sdl2.ext.Window("Hello World!", size=(96, 96))
window.show()
world = sdl2.ext.World()

texture_renderer = sdl2.ext.Renderer(window)
spriterenderer = sdl2.ext.TextureSpriteRenderSystem(texture_renderer)
world.add_system(spriterenderer)

factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=texture_renderer)
sprite = factory.from_image(RESOURCES.get_path("explosion.png"))


class MySystem(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self, renderer):
        super(MySystem, self).__init__(renderer)

    def render(self, sprite):

        ticks = sdl2.SDL_GetTicks()
        frame = int(ticks / 100 % 12)

        self._renderer.copy(sprite.texture,
                            (frame * 96, 0, 96, 96),
                            (0, 0, 96, 96))

# spriterenderer = factory.create_sprite_render_system(window)
spriterenderer = MySystem(factory.default_args["renderer"])

running = True
while running:
    spriterenderer.render(sprite)
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
    world.process()
    sdl2.SDL_Delay(20)


sdl2.ext.quit()
