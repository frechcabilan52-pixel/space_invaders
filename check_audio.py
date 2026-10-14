import pygame
import os

pygame.init()
pygame.mixer.init()

print("Checking audio...")

# Ilisi ni sa actual filename sa imong sound
sound_file = "assets/sounds/8spacesound.mp3"

if os.path.exists(sound_file):
    try:
        sound = pygame.mixer.Sound(sound_file)
        sound.play()

        print("✅ Audio file found!")
        print("🔊 Playing sound...")

        # Keep program running while sound plays
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            clock.tick(60)

    except Exception as e:
        print("❌ Error playing audio:")
        print(e)

else:
    print("❌ Audio file not found!")
    print("Expected location:")
    print(sound_file)

pygame.mixer.quit()
pygame.quit()