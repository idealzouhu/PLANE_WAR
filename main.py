import pygame
import random
import os
import pathlib

# 获取到当前文件夹的绝对路径
folder = pathlib.Path(__file__).parent.resolve()

# 游戏状态常量
FPS=60                  # 帧率
WIDIH = 500             # 游戏窗口宽度
HEIGHT = 600            # 游戏窗口高度
WHITE = (255, 255, 255)   # 背景填充颜色
GREEN = (0, 250, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

score = 0  # 玩家在游戏中的得分

# 游戏初始化（必须）
pygame.init()

# 设置主屏窗口
screen = pygame.display.set_mode((WIDIH, HEIGHT))

# 设置窗口的标题，即游戏名称
pygame.display.set_caption('飞机大战')

# 创建一个时钟对象来帮我们确定游戏要以多大的帧数运行
clock = pygame.time.Clock()

# 获取到当前文件夹的绝对路径
folder = pathlib.Path(__file__).parent.resolve()

# 加载图片和声音
background_img = pygame.image.load(os.path.join(folder, "img", "background.png")).convert()
player_img = pygame.image.load(os.path.join(folder, "img", "player.png")).convert()
rock_img = pygame.image.load(os.path.join(folder, "img", "rock.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join(folder, "img", f"rock{i}.png")).convert())

bullet_img = pygame.image.load(os.path.join(folder, "img", "bullet.png")).convert()
shoot_sound = pygame.mixer.Sound(os.path.join(folder, "sound", "shoot.wav"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join(folder, "sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join(folder, "sound", "expl1.wav"))
]
die_sound = pygame.mixer.Sound(os.path.join(folder, "sound", "rumble.ogg"))  # 飞船爆炸声音
shield_sound = pygame.mixer.Sound(os.path.join(folder, "sound", "pow0.wav"))  # 盾牌宝箱声音
gun_sound = pygame.mixer.Sound(os.path.join(folder, "sound", "pow1.wav"))  # 盾牌宝箱声音


# 加载背景音乐
pygame.mixer.music.load(os.path.join(folder, "sound", "background.ogg"))
pygame.mixer.music.set_volume(0.3)

# 加载字体
font_name = pygame.font.match_font('arial')
font_name = os.path.join(folder, 'font.ttf')

# 加载生命图片
player_mini_img = pygame.transform.scale(player_img, (25,20))
player_mini_img.set_colorkey(BLACK)

# 用字典存放爆炸特效
expl_anim = {}
expl_anim['lg'] = []  # ‘lg’:large ,  大的陨石爆炸特效
expl_anim['sm'] = []  # 'sm':small ， 小的陨石爆炸特效
expl_anim['player'] = []  # 飞船爆炸特效
for i in range(9):
    expl_img = pygame.image.load(os.path.join(folder, "img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    player_expl_img = pygame.image.load(os.path.join(folder, "img", f"player_expl{i}.png")).convert()  # 飞船爆炸特效
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)

# 用字典存放宝箱
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join(folder, "img", f"shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join(folder, "img", f"gun.png")).convert()

# 设置icon
pygame.display.set_icon(player_mini_img)


# 绘制得分
# surf:绘制到哪里， text: 绘制内容， （x,y）:坐标
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)  # 渲染
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


# 绘制血量条
def draw_health(surf, hp, x, y):
    if hp < 0 :
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100) * BAR_LENGTH  # 血量条真正长度
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT) # 血量条外框（矩形）
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)  # 血量条（矩形）
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# 绘制生命条
def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img, img_rect)


# 生成新的陨石
def new_rock():
    # 创建陨石
    rock = Rock()
    # 添加陨石角色
    all_sprites.add(rock)
    rocks.add(rock)


# 开场界面
def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, '飞机大战', 62, WIDIH/2, HEIGHT/4)
    draw_text(screen, '左右键移动飞机，空格键发射子弹', 22, WIDIH / 2, HEIGHT / 2)
    draw_text(screen, '任意键开始', 18, WIDIH / 2, HEIGHT * 3 / 4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)  # 帧率显示
        # 循环获取事件，监听事件状态
        for event in pygame.event.get():
            # 判断用户是否点了"X"关闭按钮,并执行if代码段
            # pygame.QUIT 指点击右上角窗口的"X"号
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:  # 判断事件是按下了任意键
                waiting = False
                return  False


# 飞机角色
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # 创建 一个50*40 的图像
        # self.image = pygame.Surface((50, 40))
        # self.image.fill(GREEN)
        self.image = pygame.transform.scale(player_img, (50, 40))
        self.image.set_colorkey(BLACK)  # 使飞机角色出现的多余的黑色透明
        # 设置角色轮廓
        self.rect = self.image.get_rect()
        # self.rect.center = (WIDIH/2, HEIGHT/2)
        self.rect.centerx = WIDIH/2
        self.rect.bottom = HEIGHT - 30
        # 设置飞机的圆形轮廓，使飞机和陨石碰撞自然
        self.radius = 23
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)  # 绘制圆形轮廓,注意，该代码需要放在前面才能生效

        # 设置飞机每次移动距离
        self.speedx = 8

        # 设置飞机每条生命的生命值
        self.health = 100

        # 设置飞机的生命条数
        self.lives = 3

        # 设置飞机隐藏状态
        self.hidden = False

        # 设置飞机射击子弹数量
        self.gun = 1



    def update(self):
        # 获取键盘按键
        key_pressed = pygame.key.get_pressed()

        # 获取当前事件
        current_time = pygame.time.get_ticks()

        # 根据按键移动角色
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        # 避免穿墙
        if self.rect.right > WIDIH:
            self.rect.right = WIDIH
        if self.rect.left < 0:
            self.rect.left = 0

        # 结束飞机隐身
        if self.hidden and current_time - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDIH / 2
            self.rect.bottom = HEIGHT - 30

        # 设置
        if self.gun > 1 and current_time - self.gun_time > 5000:
            self.gun = 1

    # 飞机发射子弹函数
    def shoot(self):
        if not self.hidden:
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.centery)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    # 隐藏飞机
    def hide(self):
        self.hidden = True
        self.hide_time =  pygame.time.get_ticks()
        self.rect.center = (WIDIH/2, HEIGHT+500) # HEIGHT+500即将飞机隐藏屏幕外

    # 获取宝箱后，子弹数量增加
    def gunup(self):
        self.gun = self.gun + 1
        self.gun_time = pygame.time.get_ticks()


# 陨石角色
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # 创建 一个50*40 的图
        # self.image = pygame.Surface((50, 40))
        # self.image.fill(RED)
        self.image_origin = random.choice(rock_imgs)
        self.image_origin.set_colorkey(BLACK)  # 使陨石角色出现的多余的黑色透明
        self.image = self.image_origin.copy()
        # 设置角色轮廓,随机生成不同位置的陨石
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDIH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        # 设置陨石的圆形轮廓，使飞机和陨石碰撞自然
        self.radius = self.rect.width / 2.2
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius) # 绘制圆形轮廓,注意，该代码需要放在前面才能生效

        # 设置陨石速度，使陨石左右移动
        self.speedx = random.randrange(-4, 4)
        self.speedy = random.randrange(3, 10)

        # 设置陨石旋转
        self.total_degree = 0
        self.rot_degree = 3

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # 使陨石不间断地出现在舞台
        # 当陨石接触屏幕边界后，该陨石消失，并重新生成一个新位置上的陨石
        if self.rect.top > HEIGHT or self.rect.left > WIDIH or self.rect.right < 0:
            # 设置角色轮廓,随机生成不同位置的陨石
            self.rect.x = random.randrange(0, WIDIH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            # 设置陨石速度，使陨石左右移动
            self.speedx = random.randrange(-4, 4)
            self.speedy= random.randrange(3, 10)

    def rotate(self):
        self.total_degree = self.total_degree + self.rot_degree
        self.image = pygame.transform.rotate(self.image_origin, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center


# 子弹角色
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # 创建 一个50*40 的图
        # self.image = pygame.Surface((10, 20))
        # self.image.fill(YELLOW)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)  # 使子弹角色出现的多余的黑色透明
        # 设置子弹轮廓, 子弹位置应该在飞机位置
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # 设置子弹速度，只有y坐标变换（向上移动）
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # 当子弹到达顶部时，会消失
        if self.rect.bottom < 0:
            self.kill()  # 删除克隆体


# 爆炸特效
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size  # size为 ‘lg’, 'sm'
        self.image = expl_anim[self.size][0]

        # 设置轮廓
        self.rect = self.image.get_rect()
        self.rect.center = center

        # 每次爆炸由许多张图片来实现的。图片数量用frame表示
        self.frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.frame = self.frame + 1
            if self.frame == len(expl_anim[self.size]):  # 爆炸特效图片列表播放完，  爆炸结束
                self.kill()  # 删除克隆体
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


# 宝箱
class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        # 随机生成shield, gun两种宝箱中的一种
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        # 播放宝箱声音
        if self.type == 'shield':
            shield_sound.play()
        elif self.type == 'gun':
            gun_sound.play()
        # 设置轮廓
        self.rect = self.image.get_rect()
        self.rect.center = center

        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        # 宝箱下落结束
        if self.rect.top > HEIGHT:
            self.kill()


# 固定代码段，实现点击"X"号退出界面的功能，几乎所有的pygame都会使用该段代码
show_init = True  # 显示开场画面
running = True
while running:
    # 显示开场画面
    if show_init:
        close = draw_init()
        if close:
            break
        draw_init()
        show_init = False
        # 游戏初始化
        all_sprites = pygame.sprite.Group()  # 存放所有角色的克隆体的列表
        rocks = pygame.sprite.Group()
        players = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        pygame.mixer.music.play()  # 播放背景音乐
        # 创建飞机克隆体, 添加角色
        player = Player()
        all_sprites.add(player)
        # 添加陨石，即屏幕中有8个陨石
        for i in range(8):
            # 生成新的陨石
            new_rock()
    clock.tick(FPS) # 帧率显示
    # 循环获取事件，监听事件状态
    for event in pygame.event.get():
        # 判断用户是否点了"X"关闭按钮,并执行if代码段
        # pygame.QUIT 指点击右上角窗口的"X"号
        if event.type == pygame.QUIT:
            running =False
        elif event.type == pygame.KEYDOWN:  # 判断事件是按下了某个键
            if event.key == pygame.K_SPACE:  # 判断按下了空格键
                player.shoot()  # 飞机发射子弹
    # 更新游戏
    all_sprites.update()

    # 子弹和陨石碰撞后会消失
    hits_rockandbullet = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits_rockandbullet:  # 当消灭陨石，会生成相应数量的陨石
        random.choice(expl_sounds).play()  # 播放爆炸音乐
        expl = Explosion(hit.rect.center, 'lg')  # 爆炸特效
        all_sprites.add(expl)
        new_rock()  # 生成新的陨石
        score = score + int(hit.radius)   # 计算击败陨石得分
        # 90%的概率生成宝箱
        if random.random() > 0.1:
            p = Power(hit.rect.center)
            all_sprites.add(p)
            powers.add(p)

    # 玩家和宝箱碰撞后会消失
    hits_playerandpower = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits_playerandpower: # 获取各种宝箱，并更新相应状态
        if hit.type == 'shield':
            player.health = player.health + 20
            if player.health > 100:
                player.health = 100
        elif hit.type == 'gun':
            player.gunup()

    # 玩家和陨石碰撞后会消失
    hits_playerandrock = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits_playerandrock:  # 当消灭陨石，会生成相应数量的陨石
        player.health = player.health - hit.radius
        new_rock()  # 生成新的陨石
        expl = Explosion(hit.rect.center, 'sm')  # 陨石爆炸特效
        all_sprites.add(expl)
        # 当陨石和飞机相撞后，生命值变为0时，游戏结束
        if player.health <= 0:
            death_expl = Explosion(hit.rect.center, 'player')  # 飞机爆炸特效
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives = player.lives - 1
            player.health = 100
            player.hide()
        if player.lives == 0:
            # running = False   # 结束游戏
            show_init = True  # 重新回到开始界面

    # 显示画面
    screen.fill(BLACK)  # 填充屏幕颜色
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)  # 将角色画上去
    draw_text(screen, str(score), 18, WIDIH/2, 0)  # 绘制得分
    draw_health(screen, player.health, 10, 30)  # 绘制血量条
    draw_lives(screen, player.lives, player_mini_img, WIDIH-100, 15)  # 绘制生命条
    pygame.display.update()  # 刷新屏幕

# 卸载所有模块
pygame.quit()

