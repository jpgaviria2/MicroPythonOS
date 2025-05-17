import sdl2
import sdl2.ext

sdl2.ext.init()
window = sdl2.ext.Window("Test", size=(800, 600))
window.show()

running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
        elif event.type == sdl2.SDL_KEYDOWN:
            print(f"Key pressed: {event.key.keysym.sym}")
sdl2.ext.quit()
