
# Initialize

import display_driver
import lvgl as lv

import lvgl

label = lvgl.label( lvgl.screen_active() )
label.set_text( 'hi' )

animation = lvgl.anim_t()
animation.init()
animation.set_var( label )
animation.set_values( 0, 100 )
animation.set_time( 1000 )

animation.set_custom_exec_cb( lambda not_used, value : label.set_x( value ))

#wait half a second before starting animation
animation.set_delay( 500 )

#play animation backward for 1 second after first play
animation.set_playback_time( 1000 )
#repeat animation infinitely 
animation.set_repeat_count( 10 )
#animation.set_repeat_count( lvgl.ANIM_REPEAT.INFINITE )
animation.set_repeat_delay( 500 )

animation.start()



******************************



# Initialize

import display_driver
import lvgl as lv

import lvgl

#create the slow short label
label1 = lvgl.label( lvgl.screen_active() )
label1.set_text( 'hello 1' )
label1.align( lvgl.ALIGN.CENTER, 0, -50 )

anim1 = lvgl.anim_t()
anim1.init()
anim1.set_var( label1 )
#anim1.set_time( lvgl.anim_speed_to_time( 20, 0, 100 ))
anim1.set_time( 2000 )
anim1.set_values( 0, 100 )
anim1.set_repeat_count( 10 )
anim1.set_repeat_delay( 2000 )
anim1.set_custom_exec_cb( lambda not_used, value : label1.set_x( value ))


#create the fast long label
label2 = lvgl.label( lvgl.screen_active() )
label2.set_text('hello 2')
label2.align(lvgl.ALIGN.CENTER,-100,0)

anim2 = lvgl.anim_t()
anim2.init()
anim2.set_var( label2 )
#anim2.set_time( lvgl.anim_speed_to_time( 40, -100, 100 ))
anim2.set_time(  40 * 200 )
anim2.set_values( -100, 100 )
anim2.set_custom_exec_cb( lambda not_used, value : label2.set_x( value ))
anim2.set_repeat_count( 10)
anim2.set_repeat_delay( 2000 )


#Create the fast short label
label3 = lvgl.label( lvgl.screen_active() )
label3.set_text( 'hello 3' )
label3.align( lvgl.ALIGN.CENTER, -100, 50 )


anim3 = lvgl.anim_t()
anim3.init()
anim3.set_var( label3 )
#anim3.set_time( lvgl.anim_speed_to_time( 40, -100, 0 ))
anim3.set_time(  40 * 100)
anim3.set_values( -100, 0)
anim3.set_custom_exec_cb( lambda not_used, value : label3.set_x( value ))
anim3.set_repeat_count( 10 )
anim3.set_repeat_delay(  40 * 100 + 2000 )
#anim3.set_repeat_delay( lvgl.anim_speed_to_time( 40, -100, 0) + 2000 )
#lvgl.anim_speed_to_time( 1, 2, 3)
#anim3.set_repeat_delay( 5000)
#lvgl.anim

anim1.start()
anim2.start()
anim3.start()









******************




# Initialize

import display_driver
import lvgl as lv

import lvgl

import lvgl

#normal animation
label1 = lvgl.label( lvgl.screen_active() )
label1.set_text( 'hello 1' )
label1.align( lvgl.ALIGN.CENTER, -70, -60 )

anim1 = lvgl.anim_t()
anim1.init()
anim1.set_var( label1 )
anim1.set_time( 1000 )
anim1.set_values( -70, 20 )
anim1.set_repeat_count( 100 )
anim1.set_repeat_delay( 2000 )
anim1.set_custom_exec_cb( lambda not_used, value : label1.set_x( value ))


#this animation bounces the label when it ends
label2 = lvgl.label( lvgl.screen_active() )
label2.set_text( 'hello 2' )
label2.align( lvgl.ALIGN.CENTER, 30, -60 )

anim2 = lvgl.anim_t()
anim2.init()
anim2.set_var( label2 )
anim2.set_time( 1000 )
anim2.set_values( 30, 120 )
anim2.set_custom_exec_cb( lambda not_used, value : label2.set_x( value ))
anim2.set_repeat_count( 100)
anim2.set_repeat_delay( 2000 )
anim2.set_path_cb( lvgl.anim_t.path_bounce )


#this animation goes past the end point then comes back
label3 = lvgl.label( lvgl.screen_active() )
label3.set_text( 'hello 3' )
label3.align( lvgl.ALIGN.CENTER, -70, 60 )

anim3 = lvgl.anim_t()
anim3.init()
anim3.set_var( label3 )
anim3.set_time( 1000 )
anim3.set_values( -70, 20 )
anim3.set_custom_exec_cb( lambda not_used, value : label3.set_x( value ))
anim3.set_repeat_count( 100 )
anim3.set_repeat_delay( 2000 )
anim3.set_path_cb( lvgl.anim_t.path_overshoot )


#this animation slowly starts and then slowly ends
label4 = lvgl.label( lvgl.screen_active() )
label4.set_text( 'hello 4' )
label4.align( lvgl.ALIGN.CENTER, 30, 60 )

anim4 = lvgl.anim_t()
anim4.init()
anim4.set_var( label4 )
anim4.set_time( 1000 )
anim4.set_values( 30, 120 )
anim4.set_custom_exec_cb( lambda not_used, value : label4.set_x( value ))
anim4.set_repeat_count( 100 )
anim4.set_repeat_delay( 2000 )
anim4.set_path_cb( lvgl.anim_t.path_ease_in_out )


anim1.start()
anim2.start()
anim3.start()
anim4.start()



********************




# Initialize

import display_driver
import lvgl as lv

import lvgl

button = lvgl.button( lvgl.screen_active() )
button.set_size( 50, 20 )
button.center()

anim1 = lvgl.anim_t()
anim1.init()
anim1.set_var( button )
anim1.set_time( 1000 )
anim1.set_values( -100, 100 )
anim1.set_custom_exec_cb( lambda not_used, value : button.set_x( value ))

anim2 = lvgl.anim_t()
anim2.init()
anim2.set_var( button )
anim2.set_time( 150 )
anim2.set_values( 100, 30 )
anim2.set_custom_exec_cb( lambda not_used, value : button.set_x( value ))

anim3 = lvgl.anim_t()
anim3.init()
anim3.set_var( button )
anim3.set_time( 2000 )
anim3.set_values( 30, -100 )
anim3.set_custom_exec_cb( lambda not_used, value : button.set_x( value ))

time = lvgl.anim_timeline_create()

# somehow this doesn't work:
#lvgl.anim_timeline_add( time, 0, anim1 )
#lvgl.anim_timeline_add( time, 1000, anim2 )
#lvgl.anim_timeline_add( time, 1150, anim3 )

#lvgl.anim_timeline_start( time )

