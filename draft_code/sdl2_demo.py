import sdl2
import sdl2.ext
import sdl2.sdlttf
import ctypes  # Added missing import

# Initialize SDL2 and TTF
sdl2.ext.init()
sdl2.sdlttf.TTF_Init()

# Create window and renderer
window = sdl2.ext.Window("Test", size=(800, 600))
window.show()
renderer = sdl2.ext.Renderer(window)

# Load font
font = sdl2.sdlttf.TTF_OpenFont(b"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
if not font:
    print("Failed to load font!")
    exit(1)

# Initialize text variables
last_key = "No key pressed"
text_surface = None
text_texture = None
fullscreen = False  # Track fullscreen state

def render_text(text):
    global text_surface, text_texture
    # Clean up previous texture
    if text_texture:
        sdl2.SDL_DestroyTexture(text_texture)
    
    # Create new surface and texture
    color = sdl2.SDL_Color(r=255, g=255, b=255)
    text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, text.encode('utf-8'), color)
    text_texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)

running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
        elif event.type == sdl2.SDL_KEYDOWN:
            key_name = sdl2.SDL_GetKeyName(event.key.keysym.sym).decode()
            if key_name == "F":  # Toggle fullscreen on 'F' key
                fullscreen = not fullscreen
                if fullscreen:
                    sdl2.SDL_SetWindowFullscreen(window.window, sdl2.SDL_WINDOW_FULLSCREEN)
                    sdl2.SDL_SetWindowSize(window.window, 800, 600)
                else:
                    sdl2.SDL_SetWindowFullscreen(window.window, 0)
                    sdl2.SDL_SetWindowSize(window.window, 800, 600)
                last_key = "Toggled fullscreen"
            else:
                last_key = f"Key pressed: {key_name}"
            render_text(last_key)
    
    # Clear screen
    renderer.clear()
    
    # Render text if available
    if text_texture:
        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_QueryTexture(text_texture, None, None, ctypes.byref(w), ctypes.byref(h))
        dstrect = sdl2.SDL_Rect(x=10, y=10, w=w.value, h=h.value)
        sdl2.SDL_RenderCopy(renderer.sdlrenderer, text_texture, None, dstrect)
    
    # Update display
    renderer.present()

# Cleanup
if text_texture:
    sdl2.SDL_DestroyTexture(text_texture)
if text_surface:
    sdl2.SDL_FreeSurface(text_surface)
sdl2.sdlttf.TTF_CloseFont(font)
sdl2.sdlttf.TTF_Quit()
sdl2.ext.quit()
