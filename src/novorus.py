from setup import *

while game_state['runtime']:
    # event handling
    for event in pygame.event.get():
        # checks for quit event
        if event.type == pygame.QUIT:
            game_state['runtime'] = False

    screen.fill((105, 162, 97))  # fills a surface with the rgb color

    # redraws sprites and images
    camera_group.custom_draw(player, show_hitboxes=False)
    cursor_group.draw(screen)
    light_group.render_lighting(player)

    player_bars.draw(player_group)
    enemy_bars.draw(enemy_group)

    menu.draw()
    player.inventory.draw()
    level.draw()

    # updates
    if game_state['unpaused'] and not level.transitioning:
        camera_group.update()

    cursor_group.update()
    menu.update()
    player.inventory.update()
    level.update()

    # updates screen
    pygame.display.update()
    clock.tick(60)

# closes pygame application
pygame.font.quit()
pygame.quit()

#
