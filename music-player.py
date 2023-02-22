import pygame, sys, os, random, argparse
from pygame.locals import *
pygame.init()


# ==== CONSTANTS ====
BGCOLOR          = (100, 100, 255)
TEXTBACKGROUND   = (  0,   0,   0)
WHITE            = (255, 255, 255)
BLACK            = (  0,   0,   0)
BUTTONCOLOR      = ( 30,  30,  30)
BUTTONCOLORDOWN  = ( 15,  15,  15)
TEXTCOLOR = WHITE
DISPLAYWIDTH = 500
DISPLAYHEIGHT = 200


# ==== ARGUMENTS ====

## parser object
parser = argparse.ArgumentParser()

## Add directory argument
parser.add_argument('--directory', '-d', default='./music/', help='The name of directory to use for playlist. Must be only .mp3 files. Default is "./music/"')

## Add shuffle option argument
parser.add_argument('--shuffle', '-s', action='store_true', help='Enable shuffle mode')

## Parse the arguments
args = parser.parse_args()

## Set directory according to argument
music_dir = args.directory


# ==== DISPLAY SETTINGS ====
DISPLAY = pygame.display.set_mode((DISPLAYWIDTH, DISPLAYHEIGHT))
font = pygame.font.Font("Montserrat-VariableFont_wght.ttf",  22)
btn_font = pygame.font.Font("XanhMono-Regular.ttf", 22)
icon = pygame.image.load("placa-giratoria.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Music Player")
FPS = 60
fpsClock = pygame.time.Clock()


# ==== BUTTONS AND BANNER FOR CURRENT SONG TITLE
## Top banner is a Surface so it can have alpa color
title_bg = pygame.Surface((DISPLAYWIDTH, 30))
title_bg.set_alpha(200)
title_bg.fill(TEXTBACKGROUND)

##  buttons
previous_button_rect  = pygame.Rect(100, 150, 90, 30)
pause_button_rect     = pygame.Rect(205, 150, 90, 30)
next_button_rect      = pygame.Rect(310, 150, 90, 30)


# ==== FUNCTIONS ====

## Get mp3 files recursively from selected directory
def list_files(dir_path):
    l = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if ".mp3" in file:
                file_path = os.path.join(root, file)
                l.append(file_path)
    return l

## Get the name of current song form the filename and number in playlist
# def getSongName(song_list, track_index):
#     song_name = str(track_index + 1 ) + ". " + song_list[track_index].split(".mp3")[0]
#     return song_name
def getSongName(song_list, track_index):
    song_name = str(track_index + 1 ) + ". " + song_list[track_index].split("/")[-1]
    song_name = song_name.split("mp3")[0]
    return song_name


## Print playlist in terminal
def printSongs(song_list):
    print("=========================")
    print("Song List:")
    for i in range(len(song_list)):
        print(f"{i + 1}. {song_list[i]}")
    print("=========================\n")

## Animate text in top banner so it scrolls from right to left and goes back after it is out of the window
def text_animation(text_rect):
    if text_rect.left + text_rect.width < 0:
        text_rect.left = DISPLAYWIDTH
    else:
        text_rect.left -= 1
    return text_rect.left


# ==== MAIN FUNCTION ====
def main():
    
    ## Set playlist
    file_list = list_files(music_dir)
    if args.shuffle:
        random.shuffle(file_list)
    songs = [pygame.mixer.Sound(file_name) for file_name in file_list]

    ## Set up channel for playback and play first track
    channel = pygame.mixer.Channel(0)
    current_track = pygame.mixer.Sound(songs[0])
    channel.play(current_track)
    track_index = 0
    volume = 0.5
    channel.set_volume(volume)
    track_name = getSongName(file_list, track_index)
    track_running = True

    ## Set up end_event to go to next song and loop back when playlist is finished
    end_event = pygame.USEREVENT + 1
    channel.set_endevent(end_event)

    ## Print playlist and curent song playing
    printSongs(file_list)
    print("Playing")
    print(track_name)

    ## Set up current song text for top banner
    text = font.render(getSongName(file_list, track_index), True, TEXTCOLOR)
    text_rect = text.get_rect()
    text_rect.center = (DISPLAYWIDTH / 2, 15)

    ## button default colors
    prev_btn_color = BUTTONCOLOR
    next_btn_color = BUTTONCOLOR
    pause_btn_color = BUTTONCOLOR

    ## variable for detecting whether user selected prev/next or song ended
    user_select = False


    # ==== MAIN LOOP ====
    while True:
        DISPLAY.fill(BGCOLOR)

        # ==== Event handling ====
        for event in pygame.event.get():
            ## Quit program
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()


            # ==== Key down events ====
            elif event.type == KEYDOWN:

                ## Up and down keys to increase/decrease volume
                if event.key == K_UP:
                    if volume < 1.0:
                        volume += 0.1
                        channel.set_volume(volume)
                elif event.key == K_DOWN:
                    if volume > 0:
                        volume -= 0.1
                        channel.set_volume(volume)

                ## Left and right arrow keys to go to previous and next
                elif event.key == K_RIGHT:
                    channel.stop()
                    ## go to next song, if out of playlist, go to first
                    track_index = (track_index + 1) % len(songs)
                    track = songs[track_index]
                    channel.play(track)
                    print(getSongName(file_list, track_index))
                    user_select = True
                elif event.key == K_LEFT:
                    channel.stop()
                    ## go to previous, if out of playlist, go to last
                    track_index = (track_index - 1) % len(songs)
                    track = songs[track_index]
                    channel.play(track)
                    print(getSongName(file_list, track_index))
                    user_select = True

                ## Spacebar to pause/play
                elif event.key == K_SPACE:
                    if track_running:
                        channel.pause()
                        track_running = False
                        print("Pause")
                    else:
                        channel.unpause()
                        track_running = True
                        print("Playing")


            # ==== Endevent ====
            ## If song ended, go to next, if last song ends, close program
            elif event.type == end_event:
                ## if song ended
                if not user_select:
                    # track_index = (track_index + 1) % len(songs)
                    track_index += 1
                    if track_index >= len(songs):
                        pygame.quit()
                        sys.exit()
                    else:
                        print(getSongName(file_list, track_index))
                        current_track = pygame.mixer.Sound(songs[track_index])
                        channel.play(current_track)
                ## Return variable to False is user selected
                else:
                    user_select = False


            # ==== Mouse click events ====
            ## If mouse button clicked within borders of button, change color
                ## ==> bug: if you click, then move out, button stays dark
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if previous_button_rect.collidepoint(event.pos):
                    prev_btn_color = BUTTONCOLORDOWN
                elif next_button_rect.collidepoint(event.pos):
                    next_btn_color = BUTTONCOLORDOWN
                elif pause_button_rect.collidepoint(event.pos):
                    pause_btn_color = BUTTONCOLORDOWN

            ## If mouse button released, do button's function
            elif event.type == pygame.MOUSEBUTTONUP:
                ## -Previous- button, go back
                if previous_button_rect.collidepoint(event.pos):
                    ## change button to default color
                    prev_btn_color = BUTTONCOLOR
                    ## chage track, if first song, go to last
                    track_index = (track_index - 1) % len(songs)
                    channel.stop()
                    channel.play(songs[track_index])
                    ## print song name in terminal
                    print(getSongName(file_list, track_index))
                    ## Set user_select variable True so playback doesn't jump all the way to the end
                    user_select = True
                ## -Next- button, go forward
                elif next_button_rect.collidepoint(event.pos):
                    ## change button to default color
                    next_btn_color = BUTTONCOLOR
                    ## change track, if last song, go to first
                    track_index = (track_index + 1) % len(songs)
                    channel.stop()
                    channel.play(songs[track_index])
                    ## ## print song name in terminal
                    print(getSongName(file_list, track_index))
                     ## Set user_select variable True so playback doesn't jump all the way to the end
                    user_select = True
                ## -Pause- button, stop/continue playing
                elif pause_button_rect.collidepoint(event.pos):
                    pause_btn_color = BUTTONCOLOR
                    ## If currently playing, pause
                    if track_running:
                        channel.pause()
                        track_running = False
                        print("Pause")
                    ## If currently paused, continue playback
                    else:
                        channel.unpause()
                        track_running = True
                        print("Playing")


        # ==== Draw banner and text ====

        ## render song title text
        text = font.render(getSongName(file_list, track_index), True, TEXTCOLOR)
        ## draw title banner
        DISPLAY.blit(title_bg, (0, 0))
        ## draw text
        DISPLAY.blit(text, text_rect)
        ## Start text scrolling animation
        text_rect.left = text_animation(text_rect)


        # ==== Draw buttons with text ====

        ## Draw the buttons
        pygame.draw.rect(DISPLAY, prev_btn_color, previous_button_rect)
        pygame.draw.rect(DISPLAY, pause_btn_color, pause_button_rect)
        pygame.draw.rect(DISPLAY, next_btn_color, next_button_rect)

        ## Draw text on buttons (might change for icons later)
        ### -Previous- button
        prev_text = btn_font.render("|<", True, TEXTCOLOR)
        prev_text_rect = prev_text.get_rect()
        prev_text_rect.center = previous_button_rect.center
        prev_text_rect.top -= 2
        DISPLAY.blit(prev_text, prev_text_rect)
        ### -Pause- button
        pause_text = btn_font.render("|| / >", True, TEXTCOLOR)
        pause_text_rect = pause_text.get_rect()
        pause_text_rect.center = pause_button_rect.center
        pause_text_rect.top -= 2
        DISPLAY.blit(pause_text, pause_text_rect)
        ### -Next- button
        next_text = btn_font.render(">|", True, TEXTCOLOR)
        next_text_rect = next_text.get_rect()
        next_text_rect.center = next_button_rect.center
        next_text_rect.top -= 2
        DISPLAY.blit(next_text, next_text_rect)


        # ==== Update and clock tick ====
        pygame.display.update()
        fpsClock.tick(FPS)

# ==== Run if it's the main program, not a module
if __name__ == '__main__':
    main()






# <a href="https://www.flaticon.es/iconos-gratis/musica-y-multimedia" title="musica y multimedia iconos">Musica y multimedia iconos creados por MindWorlds - Flaticon</a>
