from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate, logout
# Create your views here.
from django.urls import reverse
from django.views import View
from goods.models import Goods
from user.models import  User
from django.http import Http404
# todo   场景 :  再注册是 选这号身份 ， d对不通身份进行分组， 身份不同对应的权限也就不同



class Register(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'test/register.html')

    def post(self, request, *args, **kwargs):
        """
        先创建组名
        """
        try:
            merchant=Group.objects.create(name='商家')
            customer=Group.objects.create(name='顾客')
            StaffService=Group.objects.create(name='人工客服')
        except Exception as s:
            merchant = Group.objects.get(name='商家')
            customer = Group.objects.get(name='顾客')
            StaffService = Group.objects.get(name='人工客服')

        #因为组没有权限 所以为其绑定用户 并给用户分配权限
        '''   也可以直接给组加权限    '''
        # 1 给用户 分配权限    auth_permission  中 codename（权限名称）
        #  1.1这里设置用户(商家) 对商品又那些权限
        '''merchant_permission=Permission.objects.create(Q(codename__endswith='_goods')   #观察权限表 这样写表示有用对商品的增删改查所以权限
                                                  |  Q(codename__endswith='_message') # 同理 对消息 可以增删改查
                                                  |  Q(codename__endswith='view_order')   #订单查看权限
                                                  |  Q(codename__endswith='change_order') #订单查看修改
                                                  | Q(codename__endswith='view_address')
                                                  |  Q(codename__endswith='change_address') )
        # 1.2 客服
        StaffService_permission = Permission.objects.create(Q(codename__endswith='view_goods')  # 观察权限表 这样写表示有用对商品的增删改查所以权限
                                                        | Q(codename__endswith='_message')  # 同理 对消息 可以增删改查
                                                        | Q(codename__endswith='view_order')  # 订单查看权限

                                                        | Q(codename__endswith='view_address')
                                                       )
        # 1.3 用户
        user_permission =Permission.objects.create(Q(codename__endswith='view_goods')   #观察权限表 这样写表示有用对商品的增删改查所以权限
                                                  |  Q(codename__endswith='_message') # 同理 对消息 可以增删改查
                                                  |  Q(codename__endswith='view_order')   #订单查看权限
                                                  |  Q(codename__endswith='change_order') #订单查看修改
                                                  | Q(codename__endswith='_address')
                                                   
                                                )'''
        merchant_permission = Permission.objects.filter(Q(codename__endswith='_goods')  | Q(codename__endswith='_message')   | Q(codename='view_order') | Q(codename='change_order') | Q(codename='view_address')   | Q(codename='change_address'))

        # 1.2 客服
        StaffService_permission = Permission.objects.filter(
            Q(codename='view_goods')  # 观察权限表 这样写表示有用对商品的增删改查所以权限
            | Q(codename__endswith='_message')  # 同理 对消息 可以增删改查
            | Q(codename='view_order')  # 订单查看权限

            | Q(codename='view_address')
            )
        # 1.3 用户
        user_permission = Permission.objects.filter(Q(codename='view_goods')  # 观察权限表 这样写表示有用对商品的增删改查所以权限
                                                    | Q(codename__endswith='_message')  # 同理 对消息 可以增删改查
                                                    | Q(codename='view_order')  # 订单查看权限
                                                    | Q(codename='change_order')  # 订单查看修改
                                                    | Q(codename__endswith='_address') )



        # 2 将权限  直接接入到组里面 ( 组里的用户拥有组的所有权限)
        #  之所以将 权限直接加入组里 是 某个身份的人拥有同意的权限 （又一些用户 可以又特殊权限 则单独对用户权限修改）
        merchant.permissions.add(*merchant_permission)   #将商家权限加入商家组 （所有再商家组的 用户同意拥有 商家权限）
        customer.permissions.add(*user_permission)  # 同上
        StaffService.permissions.add(*StaffService_permission)  # 同上

        # 3. 获得注册信息
        username=request.POST.get('username')
        password=request.POST.get('password')
        identity=request.POST.get('identity')
        print(identity)
        if not all(username and password and identity):
            return HttpResponse('请填写全部信息')
        user=User.objects.filter(username=username).exists()
        if user:
            return HttpResponse('用户已存在')



######################################################################################################################################
        # 注册成功
        us=User.objects.create_user(username=username,password=password,flag=identity)
        if us.username == 'zs1':
            us.groups.add(customer)   #  有权限但 不是 商家组
            us.user_permissions.add(*Permission.objects.filter(Q(codename='change_goods')  | Q(codename='add_goods')))
            us.save()
            return HttpResponse('张三可以删除商品')

        if us.username == 'zs2':

            # 这样写 无法将 用户加入 组中
            us.groups.add( merchant.permissions.add(*Permission.objects.filter(Q(codename='view_goods'))))  # 是 商家组

            us.user_permissions.add(*Permission.objects.filter(Q(codename='view_goods') ))  # 但没权限
            # todo  没实现 因为他是再 商家组里，所有还是用有商家组的所有权限 has_prams 会检查到 返回True
            us.save()
            return HttpResponse('张三可以看商品')


        # todo  这部分想实现 在商家组里 但 有不同权限  ,权限是可以分配成功  ，并且（用户权限表也是对的） ， 但是 一位你再商家组里， 所以 has_perms依然判断你是有 商家组所有权限的
        if us.username == 'zs3':
            us.groups.add(merchant)  # 是 商家组

            # 创建自定义权限
            custom_permission = Permission.objects.create(
                name='Can perform custom action',
                codename='zdyqx',
                content_type=ContentType.objects.get_for_model(User)
            )
            us.user_permissions.add(custom_permission)   #

            us.save()
            return HttpResponse('张三可以看商品')
        if us.username == 'zs4':
            us.groups.add(merchant)  # 是 商家组


            us.user_permissions.add(* merchant_permission)
            us.user_permissions.remove(*Permission.objects.filter(codename='change_goods'))  #移除一个权限
            us.save()
            return HttpResponse('张三移除一个权限')

        if us.username == 'zs5':
            mer = merchant.permissions.remove(
                Permission.objects.filter(Q(codename='change_goods') | Q(codename='add_goods')))  # 移除组的某个权限

            us.groups.add(mer)  # 是 商家组

           #  不继承组的权限
            us.user_permissions.remove(*Permission.objects.filter(Q(codename='change_goods')  | Q(codename='add_goods')))  # 移除 用户 一个权限
            us.save()
            us.user_permissions.add(*merchant_permission)  #在加入权限组





            return HttpResponse('张三继承组的权限')
        # todo  上面的 不管 移除组的权限  还是移除用户的权限 都无法实现 ，移除在的权限 只能将其放入一个新的组，移除用户权限，但组的权限还在，依然无效
        # 所有如果真想实现 区分普通商家 和达人商家  (方法1： 那就将普通商家和达人商家 分别放到不同的组，
        #                                   f2 : 在写判断时只对权限进行判断，不判断其 所属组，
        #                                   那么这是就可以结合身份标识一起使用，不全时普通还是达人商家，标识都是商家 ，不结合标识一样可以 )

########################################################################################################################
        # 根据用户注册是德操作 ，将用户分到不同的组中，从而实现权限的管理
        # 给用户分组
        identity=int(identity)
        if identity==1:
            #则将其加到用户组 拥有用户的所有权限
            us.groups.add(customer)
            # 地区 将用户加入到某个组 ，并不能直接继承 ，还需要自己为其分配权限
            # 意思说 : 组用有的权限 不一定 全部分配给你 就算组没有的 权限 我也可以自己添加
            # 将其分到组里 也就是一个权限集合 可以一次性继承它的所有权限,无需给每个用户取添加权限 ，(也就是物以类聚，人以群分)
            us.user_permissions.add(* user_permission)
            us.save()
            print('将权限加入 用户组')
            return  HttpResponse('将权限加入 用户组')
        if identity==2:
            # 则将其加到商家组 拥有商家的所有权限
            us.groups.add(merchant)
            # 这里是直接继承啦 商家住的所有权限  (但是同商家 有不同 权限  达人商家 普通商家 再同一组用 不同权限)
            us.user_permissions.add(* merchant_permission)   # 所有再分配权限是 可以不继承组的所有权限 ，或者继承后 减去某个权限 或 加商其他权限 都可以
            us.save()
            print('将权限加入 商家组')
            return HttpResponse('将权限加入 商家组')
        if identity==3:
            # 则将其加到客服组 拥有客服的所有权限
            us.groups.add(StaffService) #  #加入组
            us.user_permissions.add(* StaffService_permission)  #获得住的所有权限
            us.save()
            print('将权限加入 客服组')
            return HttpResponse('将权限加入 客服组')

        # 完成啦 分组 注册 ！！！！！！！！！！！！！
        return HttpResponse('注册及权限添加完成！！！！！！！！！！！！！！！')

class Login(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'test/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not all(username and password):
            return HttpResponse('请填写全部信息')
        user=authenticate(username=username,password=password)
        if not user:
            return HttpResponse('用户名密码错')
        request.session['user_id']=user.id
        #不在登录这里 做任何判断 ，不管是谁都可以登入进入同一个首页
        return redirect('/index/')

class Logout(View):
    def get(self,request):
        logout(request)
        return redirect('/login/')


class Index(View):
    def get(self, request, *args, **kwargs):
        goods=Goods.objects.all()
        print(goods)
        return render(request, 'test/index.html', context={'goods':goods})

class GoodsView(View):
    """
     不管。正式业务逻辑
    """
    def get(self, request, *args, **kwargs):
        user_id=request.session.get('user_id')
        user=User.objects.filter(id=user_id).first()
        print(user.flag)
        flag=int(user.flag)
        # 不能只 判断分组 （如果这样 跟给用户加标识有什么区别 ？）
        # 商家用于用户的所有权限 （唯独不能没直接的商品 ）
        # 用户 标识 为 1  所有就算给你权限 也进不来
        # 当然用户 可以 变成商家 则标识也变为 2 (用户变为商家 就默认加入商家 组 ,这就是为什么要分组)
        # 所以说再不同的组有不同的权限 ,当 商家 变为 用户 则从 商家组中将其移除 那就没有啦商家组的权限 (也有可能 只是变标识,保留你的开店记录，也在再开就变标识，就不用再去变更组和权限)
        # print('--------------------',user.groups.all())

        # 其实这里也可以根据标识 判断 flag

        # todo  根据情况来 不一定要两 层 判断
        if  not  user.groups.filter(name='商家').exists():   # 这里 先判断是否是商家 ( 第一层判断)
            return HttpResponse('抱歉没有权限你不是商家！！！！！！！！')
        # has_perms = user.has_perm('goods.change_goods')
        print('用户有那些权限:',user.user_permissions.all())
        has_perms=user.has_perms(['goods.change_goods','goods.add_goods'])
        print(has_perms)  # 打印返回值

        # 为什么要分权限
        if not has_perms:  # 你是商家 但你肯只是普通商家 有些达人商家的权限 你并没有用用于 ( 第二层判断 )
            return HttpResponse('抱歉没有权限！！！！！！！！')


        idx=request.GET.get('id')
        goods = Goods.objects.filter(id=idx).first()
        print(idx)

        return render(request, 'test/edit.html', context={'goods': goods})


    def  post(self,request,*args,**kwargs):
        user_id = request.session.get('user_id')
        user = User.objects.filter(id=user_id).first()
        print('------------------------')
        # print( user_id )
        fla=int(user.flag)

        if  not user.groups.filter(name='商家').exists():  # 这里 先判断是否是商家 ( 第一层判断)
            return HttpResponse('抱歉没有权限你不是商家！！！！！！！！')
        has_perms = user.has_perms(['goods.change_goods', 'goods.add_goods'])
        print(has_perms)  # 打印返回值
        """
        如果一个用户没有直接分配某个权限，但他所在的组拥有这个权限，那么has_perms方法会返回True。这是因为用户通过组继承了组的权限
        """
        if not has_perms:
            return HttpResponse('抱歉没有权限！！！！！！！！')

        goods_names=request.POST.get('goods_name')
        price=request.POST.get('price')
        if not all( [goods_names and price]):
            return HttpResponse('请填写全部信息')
        # Goods.objects.create(goods_name=goods_names,price=price)
        # return redirect('/index/')

        #

        Goods.objects.create(goods_name=goods_names, price=price)
        return redirect('/index/')


"""
    用户    变   商家
    us.groups.add(merchant)   #加入商家组
    us.user_permissions.add(merchant_permissions) 绑定权限
    us.flag=2
    这时用户即在商家组有在用户组 (唯一不能买自己商品,)
    
    商家 变     用户 
     
    # 获取组对象  
    group = Group.objects.get(name='商家')  
    # 获取用户对象  
    user = User.objects.get(username='zs')  
    # 从组中移除用户  
    group.user_set.remove(user) # 那么商家 zs 就不在 商家组了  （# 确保用户不从组中继承权限  us.groups.clear()  # 从用户所在的组中移除用户 ）
    
    # 这里不要想着被篡改 权限 不在商家 组 那就不会用于商家组的权限（用户加组时， 只是将组的权限分配给他, 并没有直接加给用户本身，当年离开啦组个组，那就不会在用户这个组的权限）
    
    
    
    
      

"""

class DeleteGoods(View):
    pass




#个人中心 (   )
def UserInfo():
    """
    1。 如果是商家 个人中心就会
    有 商品管理  按钮 （当然这里商品管理界面只有商家自己，可以进入 ,
    可以查看,每个店的风格和商品都不一样 , ） 其他界面权限都一样
    # 情况 :  接口暴露， (是否用户账号也能登录进商家管理界面 ? ) ,
    这时权限起作用啦,没有用户的账号不再商家组里，没有登录进去的权限,
    权益控制是一种 , 用户身份标识也是一种方法(当然不是简单的标记,这样写一样可以实现,商品管理界面身份校验不成功当然登录不了，跟别说登录后德操作)

    #  分表可以吗 ?
    #    可以 ( 从商家 变为 用户  或反之    ,商家也是用户,当每个用户满足某些添加这 再商家表中 新增数据 ,  或者想某个条件 ，商家表将其状态 改掉 （不是物理删除）  )

    """


# 只针对  django用户权限与分组的实现  ，








































