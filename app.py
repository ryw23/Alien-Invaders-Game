"""
Primary module for Alien Invaders

This module contains the main controller class for the Alien Invaders application. There 
is no need for any additional classes in this module.  If you need more classes, 99% of 
the time they belong in either the wave module or the models module. If you are unsure 
about where a new class should go, post a question on Piazza.

Ray Wei (ryw23) and Andrew Tsai (aht53)
Completed 12/8/17

Portion of input code inspired by state.py demo
Author: Walker M. White

EXTENSIONS:
Animated alien movement and death
Added multiple endless waves and wave counter
Added missile feature, which had different bolt color, speed, and conditions for deletion
Added sound effects and background music with mute feature
Added dynamic alien speed based on aliens killed as well as wave count
Added HUD with missile count, lives count, wave count
Added background image and instructions in title screen

"""
import cornell
from consts import *
from game2d import *
from wave import *


# PRIMARY RULE: Invaders can only access attributes in wave.py via getters/setters
# Invaders is NOT allowed to access anything in models.py

class Invaders(GameApp):
    """
    The primary controller class for the Alien Invaders application
    
    This class extends GameApp and implements the various methods necessary for processing 
    the player inputs and starting/running a game.
    
        Method start begins the application.
        
        Method update either changes the state or updates the Play object
        
        Method draw displays the Play object and any other elements on screen
    
    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the start method instead.  This is only for this class.  All other classes
    behave normally.
    
    Most of the work handling the game is actually provided in the class Wave.
    Wave should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.
    
    The primary purpose of this class is to manage the game state: which is when the 
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.
    
    INSTANCE ATTRIBUTES:
        view:   the game view, used in drawing (see examples from class)
                [instance of GView; it is inherited from GameApp]
        input:  the user input, used to control the ship and change state
                [instance of GInput; it is inherited from GameApp]
        _state: the current state of the game represented as a value from consts.py
                [one of STATE_INACTIVE, STATE_NEWWAVE, STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, STATE_COMPLETE]
        _wave:  the subcontroller for a single wave, which manages the ships and aliens
                [Wave, or None if there is no wave currently active]
        _text:  the currently active message
                [GLabel, or None if there is no message to display]
    
    STATE SPECIFIC INVARIANTS: 
        Attribute _wave is only None if _state is STATE_INACTIVE.
        Attribute _text is only None if _state is STATE_ACTIVE.
    
    For a complete description of how the states work, see the specification for the
    method update.
    
    You may have more attributes if you wish (you might want an attribute to store
    any score across multiple waves). If you add new attributes, they need to be 
    documented here.
    
    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY:
        _text2:  the second currently active message [GLabel or None]
        _last:   the variable that ensures that once a key is pressed and held, the
                 function associated with that button executes only once [int >= 0]
        _mlast:  the variable that ensures that once the mute key is pressed and held, the
                 function associated with that button executes only once [int >= 0]
        _speedMod: the modifier to increase alien speed between waves [double > 0]
        _waveCount: the number of the current wave [int >= 1]
        _background: the background image [GImage]
        _song:   the background music [Sound]
        _volume: the multiplier for volume of all sounds and music [double >= 0]
        
    """
    
    # DO NOT MAKE A NEW INITIALIZER!
    
    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.
        
        This method is distinct from the built-in initializer __init__ (which you 
        should not override or change). This method is called once the game is running. 
        You should use it to initialize any game specific attributes.
        
        This method should make sure that all of the attributes satisfy the given 
        invariants. When done, it sets the _state to STATE_INACTIVE and create a message 
        (in attribute _text) saying that the user should press to play a game.
        """
        # IMPLEMENT ME
        self._state = STATE_INACTIVE
        self._wave = None
        self.welcomeMessage()
        self._last = 0
        self._text2 = GLabel(text = '')
        self._speedMod = ALIEN_SPEED
        self._waveCount = 1
        self._background = GImage(x = GAME_WIDTH/2, y = GAME_HEIGHT/2,
                                  width = GAME_WIDTH, height = GAME_HEIGHT, source = 'Background5.png')
        self.instructionsText()
        self._song = Sound('Superboy.mp3')
        self._volume = GAME_VOLUME
        self._song.volume = SONG_VOLUME
        self._song.play(True)
        self._mlast = 0


    def update(self,dt):
        """
        Animates a single frame in the game.
        
        It is the method that does most of the work. It is NOT in charge of playing the
        game.  That is the purpose of the class Wave. The primary purpose of this
        game is to determine the current state, and -- if the game is active -- pass
        the input to the Wave object _wave to play the game.
        
        As part of the assignment, you are allowed to add your own states. However, at
        a minimum you must support the following states: STATE_INACTIVE, STATE_NEWWAVE,
        STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, and STATE_COMPLETE.  Each one of these 
        does its own thing and might even needs its own helper.  We describe these below.
        
        STATE_INACTIVE: This is the state when the application first opens.  It is a 
        paused state, waiting for the player to start the game.  It displays a simple
        message on the screen. The application remains in this state so long as the 
        player never presses a key.  In addition, this is the state the application
        returns to when the game is over (all lives are lost or all aliens are dead).
        
        STATE_NEWWAVE: This is the state creates a new wave and shows it on the screen. 
        The application switches to this state if the state was STATE_INACTIVE in the 
        previous frame, and the player pressed a key. This state only lasts one animation 
        frame before switching to STATE_ACTIVE.
        
        STATE_ACTIVE: This is a session of normal gameplay.  The player can move the
        ship and fire laser bolts.  All of this should be handled inside of class Wave
        (NOT in this class).  Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.
        
        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen.
        
        STATE_CONTINUE: This state restores the ship after it was destroyed. The 
        application switches to this state if the state was STATE_PAUSED in the 
        previous frame, and the player pressed a key. This state only lasts one animation 
        frame before switching to STATE_ACTIVE.
        
        STATE_COMPLETE: The wave is over, and is either won or lost.
        
        You are allowed to add more states if you wish. Should you do so, you should 
        describe them here.
        
        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        # IMPLEMENT ME
        self.welcomeMessage()
        if self._state == STATE_INACTIVE:
            self.buttonPress()
            self.instructionsText()
        if self._state == STATE_NEWWAVE:
            self._wave = Wave()
            self._state = STATE_ACTIVE
        if self._state == STATE_ACTIVE:
            initiallives = self._wave.getLives()
            self._wave.waveUpdate(self.input, dt, self._speedMod, self._volume)
            if self._wave.getWinLose() == 1:
                self._state = STATE_WON
                self.welcomeMessage()
                self._waveCount += 1
            elif self._wave.getLives() != initiallives and self._wave.getLives() > 0:
                self._state = STATE_PAUSED
                self.welcomeMessage()
            elif self._wave.getLives() == 0:
                self._wave.setWinLose(0)
                self._state = STATE_LOST
                self._waveCount = 1
                self.welcomeMessage()
        if self._state == STATE_PAUSED:
            self.spacePress()
        if self._state == STATE_CONTINUE:
            self._wave.setCont(1)
            self._state = STATE_ACTIVE
        if self._state == STATE_WON:
            self.buttonPress()
        if self._state == STATE_LOST:
            self.buttonPress()
            self._speedMod = ALIEN_SPEED
        self.muter()
            

    def draw(self):
        """
        Draws the game objects to the view.
        
        Every single thing you want to draw in this game is a GObject.  To draw a GObject 
        g, simply use the method g.draw(self.view).  It is that easy!
        
        Many of the GObjects (such as the ships, aliens, and bolts) are attributes in 
        Wave. In order to draw them, you either need to add getters for these attributes 
        or you need to add a draw method to class Wave.  We suggest the latter.  See 
        the example subcontroller.py from class.
        """
        # IMPLEMENT ME
        self._background.draw(self.view)
        if self._state == STATE_INACTIVE:
            self._instructs1.draw(self.view)
            self._instructs2.draw(self.view)
            self._instructs3.draw(self.view)
            self._instructs4.draw(self.view)
            self._instructs5.draw(self.view)
            self._text.draw(self.view)
            self._text2.draw(self.view)
        if self._state == STATE_LOST:
            self._text.draw(self.view)
            self._text2.draw(self.view)
        if (self._state == STATE_NEWWAVE or self._state == STATE_ACTIVE
            or self._state == STATE_CONTINUE):
            self._wave.waveDraw(self.view)
            self.displayWavesText()
            self._displayWavesText.draw(self.view)
        if self._state == STATE_PAUSED:
            self.displayWavesText()
            self._wave.waveDraw(self.view)
            self._text.draw(self.view)
            self._displayWavesText.draw(self.view)
        if self._state == STATE_WON:
            self._text.draw(self.view)
            self._text2.draw(self.view)
            
            
    def welcomeMessage(self):
        """
        Sets the active message to be displayed depending on the value of _state
        
        Since the game has to display different messages depending on which part
        of the game is currently running, this helper method is needed for that
        functionality (i.e. none for STATE_ACTIVE, "congratulations" for
        STATE_WON, etc.).
        
        Parameters: none
        """
        if self._state == STATE_ACTIVE:
            self._text = None
        elif self._state == STATE_PAUSED:
            self.pausedText()
        elif self._state == STATE_LOST:
            self.lostText()
        elif self._state == STATE_WON:
            self.wonText()
        elif self._state == STATE_INACTIVE:
            self._text = GLabel(text = "Press Enter to Start")
            self._text.font_size = 40
            self._text.x = GAME_WIDTH/2
            self._text.y = GAME_HEIGHT/2 + 10
            self._text.font_name = 'RetroGame.ttf'
            self._text.linecolor = 'green'
            self._text2 = GLabel(text = "Alien Invaders")
            self._text2.font_size = 60
            self._text2.x = GAME_WIDTH/2
            self._text2.y = GAME_HEIGHT/2 + 100
            self._text2.font_name = 'RetroGame.ttf'
            self._text2.linecolor = 'green'

            
    def buttonPress(self):
        """
        Function to handle the input specifically for "enter"
        
        The "enter" button is used specifically for starting the game from the
        starting screen as well as for restarting a game after losing. This
        function is inspired by the determineState method from state.py written
        by Walker M. White. It is to ensure that when the enter button is pressed,
        only the first input registers and changes the state; any subsequent
        input readings from the button being held will not alter the state.
        
        This function also serves the purpose of speeding up the aliens by a
        factor of 0.85 (stored in self._speedMod) every time a wave is completed
        and a new one is started.
        
        Parameters: None
        """
        current = self.input.key_count
        currentkey = self.input.is_key_down('enter')
        if current > 0 and self._last == 0 and currentkey and self._state == STATE_WON:
            self._state = STATE_NEWWAVE
            self._speedMod = self._speedMod * .85
        elif current > 0 and self._last == 0 and currentkey:
            self._state = STATE_NEWWAVE
        self._last = current
        
        
    def spacePress(self):
        """
        Function to handle the input specifically for "spacebar"
        
        The "spacebar" button is used to start a new life once one is lost and
        the game is momentarily paused.
        
        Parameters: None
        """
        current = self.input.key_count
        currentkey = self.input.is_key_down('spacebar')
        if current > 0 and self._last == 0 and currentkey:
            self._state = STATE_CONTINUE
        self._last = current
        
            
    def displayWavesText(self):
        """
        Function to set the wave counter's attributes
        
        The wave counter in the game displays the current wave, or level, that
        the player is on. It increases by one every time an entire wave is eliminated
        and a new wave is started, and resets back to one once the player loses the
        game.
        
        Parameters: None
        """
        self._displayWavesText = GLabel(text = 'Wave ' + str(self._waveCount))
        self._displayWavesText.font_size = 20
        self._displayWavesText.x = 50
        self._displayWavesText.y = GAME_HEIGHT - 15
        self._displayWavesText.font_name = 'RetroGame.ttf'
        self._displayWavesText.linecolor = 'green'
        
        
    def instructionsText(self):
        """
        Function to set the game instructions
        
        The game instructions are displayed on the title screen, and tell the player
        how to fire, move, and mute the music/sounds in the game.
        
        Parameters: None
        """
        self._instructs1 = GLabel(text = 'Controls:')
        self._instructs1.font_size = 30
        self._instructs1.x = GAME_WIDTH/2; self._instructs1.y = GAME_HEIGHT/2 - 25
        self._instructs1.font_name = 'RetroGame.ttf'
        self._instructs1.linecolor = 'green'
        self._instructs2 = GLabel(text = 'SPACE to shoot')
        self._instructs2.font_size = 20
        self._instructs2.x = GAME_WIDTH/2; self._instructs2.y = GAME_HEIGHT/2 - 55
        self._instructs2.font_name = 'RetroGame.ttf'
        self._instructs2.linecolor = 'green'
        self._instructs3 = GLabel(text = 'UP arrow key to fire missile')
        self._instructs3.font_size = 20
        self._instructs3.x = GAME_WIDTH/2; self._instructs3.y = GAME_HEIGHT/2 - 80
        self._instructs3.font_name = 'RetroGame.ttf'
        self._instructs3.linecolor = 'green'
        self._instructs4 = GLabel(text = 'LEFT AND RIGHT arrow keys to move')
        self._instructs4.font_size = 20
        self._instructs4.x = GAME_WIDTH/2; self._instructs4.y = GAME_HEIGHT/2 - 105
        self._instructs4.font_name = 'RetroGame.ttf'
        self._instructs4.linecolor = 'green'
        self._instructs5 = GLabel(text = 'M to mute music')
        self._instructs5.font_size = 20
        self._instructs5.x = GAME_WIDTH/2; self._instructs5.y = GAME_HEIGHT/2 - 130
        self._instructs5.font_name = 'RetroGame.ttf'
        self._instructs5.linecolor = 'green'
        
        
    def lostText(self):
        """
        Sets the message for when the state is STATE_LOST
        
        This is called only in the helper function welcomeMessage above; it
        sets the active text to "GAME OVER" and a subtitle under it that
        says "HIT ENTER TO RESTART," to allow the player to replay the game
        (restart from wave 1).
        
        Parameters: None
        """
        self._text = GLabel(text = "GAME OVER")
        self._text.font_size = 100
        self._text.x = GAME_WIDTH/2
        self._text.y = GAME_HEIGHT/2 + 25
        self._text.font_name = 'RetroGame.ttf'
        self._text.linecolor = 'green'
        self._text2 = GLabel(text = 'Hit Enter to Restart')
        self._text2.font_size = 40
        self._text2.x = GAME_WIDTH/2
        self._text2.y = GAME_HEIGHT/2 - 40
        self._text2.font_name = 'RetroGame.ttf'
        self._text2.linecolor = 'green'
        
        
    def wonText(self):
        """
        Sets the message for when the state is STATE_WON
        
        This is called only in the helper function welcomeMessage above; it
        sets the active text to "CONGRATULATIONS" and a subtitle under it that
        says "HIT ENTER FOR NEXT WAVE," to allow the player to continue to the
        next wave/level.
        
        Parameters: None
        """
        self._text = GLabel(text = '**YOU WIN**')
        self._text2 = GLabel(text = 'Hit Enter for Next Wave')
        self._text.font_size = 100
        self._text.x = GAME_WIDTH/2
        self._text.y = GAME_HEIGHT/2 + 40
        self._text.font_name = 'RetroGame.ttf'
        self._text.linecolor = 'green'
        self._text2.font_size = 40
        self._text2.x = GAME_WIDTH/2
        self._text2.y = GAME_HEIGHT/2 - 35
        self._text2.font_name = 'RetroGame.ttf'
        self._text2.linecolor = 'green'
        
        
    def pausedText(self):
        """
        Sets the message for when the state is STATE_PAUSED
        
        This is called only in the helper function welcomeMessage above; it
        sets the active text to "Press Space to Continue", which lets the player
        know how to continue when they have lost a life.
        
        Parameters: None
        """
        self._text = GLabel(text = "Press Space to Continue")
        self._text.font_size = 40
        self._text.x = GAME_WIDTH/2
        self._text.y = GAME_HEIGHT/2
        self._text.font_name = 'RetroGame.ttf'
        self._text.linecolor = 'green'
        
        
    def muter(self):
        """
        This function toggles sound for the game on and off
        
        If the current game volume is on (for both background music and sounds)
        then pressing 'm' will mute the game (set the volumes to zero). If the
        game is muted, then pressing 'm' will change the volumes back to their
        original values.
        
        Parameters: None
        """
        current = self.input.key_count
        currentkey = self.input.is_key_down('m')
        if current > 0 and self._mlast == 0 and currentkey and self._song.volume != 0:
            self._volume = 0
            self._song.volume = 0
        elif current > 0 and self._mlast == 0 and currentkey and self._song.volume == 0:
            self._volume = GAME_VOLUME
            self._song.volume = SONG_VOLUME
        self._mlast = current
    # HELPER METHODS FOR THE STATES GO HERE