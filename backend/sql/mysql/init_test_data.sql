insert into sys_dept (id, name, level, sort, leader, phone, email, status, del_flag, parent_id, created_time, updated_time)
values  (1, 'test', 0, 0, null, null, null, 1, 0, null, '2023-06-26 17:13:45', null);

insert into sys_api (id, name, method, path, remark, created_time, updated_time)
values  (1, '创建API', 'POST', '/api/v1/apis', null, '2024-02-02 11:29:47', null),
        (2, '删除API', 'DELETE', '/api/v1/apis', null, '2024-02-02 11:31:32', null),
        (3, '编辑API', 'PUT', '/api/v1/apis/{pk}', null, '2024-02-02 11:32:22', null);

INSERT INTO sys_menu (id, title, NAME, LEVEL, menu_type, perms, STATUS, display, CACHE, parent_id, created_time, is_admin)
VALUES-- ################################  平台端  #########################
        (1, '工作台', 'Workplace', 0, 0, NULL, 1, 1, 1, NULL, NOW(), 1),
        (2, '商户管理', 'Store', 0, 0, NULL, 1, 1, 1, NULL, NOW(), 1),
        (21, '系统管理', 'System', 0, 0, NULL, 1, 1, 1, NULL, NOW(), 1),
        (22, '系统监控', 'monitor', 0, 0, NULL, 1, 1, 1, NULL, NOW(), 1),
        (23, '日志', 'log', 0, 0, NULL, 1, 1, 1, NULL, NOW(), 1),
        (2010, '商户列表', 'StoreList', 1, 1, 'tenant:store:list', 1, 1, 1, 2, NOW(), 1),
        (2011, '商户查询', 'StoreQuery', 2, 2, 'tenant:store:query', 1, 1, 1, 2010, NOW(), 1),
        (2012, '商户新增', 'StoreAdd', 2, 2, 'tenant:store:add', 1, 1, 1, 2010, NOW(), 1),
        (2013, '商户删除', 'StoreDel', 2, 2, 'tenant:store:del', 1, 1, 1, 2010, NOW(), 1),
        (2014, '商户编辑', 'Storeupdate', 2, 2, 'tenant:store:edit', 1, 1, 1, 2010, NOW(), 1),
        (2110, '部门管理', 'SysDept', 1, 1, 'sys:dept:list', 1, 1, 1, 21, NOW(), 1),
        (2111, '部门查询', 'QueryDept', 2, 2, 'sys:dept:query', 1, 1, 1, 2110, NOW(), 1),
        (2112, '部门新增', 'AddDept', 2, 2, 'sys:dept:add', 1, 1, 1, 2110, NOW(), 1),
        (2113, '部门删除', 'DelDept', 2, 2, 'sys:dept:del', 1, 1, 1, 2110, NOW(), 1),
        (2114, '部门更新', 'UpdateDept', 2, 2, 'sys:dept:edit', 1, 1, 1, 2110, NOW(), 1),
        (2120, '用户管理', 'SysUser', 1, 1, 'sys:user:list', 1, 1, 1, 21, NOW(), 1),
        (2121, '用户查询', 'QueryUser', 2, 2, 'sys:user:query', 1, 1, 1, 2120, NOW(), 1),
        (2122, '用户新增', 'AddUser', 2, 2, 'sys:user:add', 1, 1, 1, 2120, NOW(), 1),
        (2123, '用户删除', 'DelUser', 2, 2, 'sys:user:del', 1, 1, 1, 2120, NOW(), 1),
        (2124, '用户修改', 'UpdateUser', 2, 2, 'sys:user:edit', 1, 1, 1, 2120, NOW(), 1),
        (2130, '角色管理', 'SysRole', 1, 1, 'sys:role:list', 1, 1, 1, 21, NOW(), 1),
        (2131, '角色查询', 'AueryRole', 2, 2, 'sys:role:query', 1, 1, 1, 2130, NOW(), 1),
        (2132, '角色新增', 'AddRole', 2, 2, 'sys:role:add', 1, 1, 1, 2130, NOW(), 1),
        (2133, '角色删除', 'DelRole', 2, 2, 'sys:role:del', 1, 1, 1, 2130, NOW(), 1),
        (2134, '角色修改', 'UpdateRole', 2, 2, 'sys:role:edit', 1, 1, 1, 2130, NOW(), 1),
        (2140, '菜单管理', 'SysMenu', 1, 1, 'sys:menu:list', 1, 1, 1, 21, NOW(), 1),
        (2141, '菜单查询', 'QueryMenu', 2, 2, 'sys:menu:query', 1, 1, 1, 2140, NOW(), 1),
        (2142, '菜单新增', 'AddMenu', 2, 2, 'sys:menu:add', 1, 1, 1, 2140, NOW(), 1),
        (2143, '菜单删除', 'DelMenu', 2, 2, 'sys:menu:del', 1, 1, 1, 2140, NOW(), 1),
        (2144, '菜单修改', 'UpdateMenu', 2, 2, 'sys:menu:edit', 1, 1, 1, 2140, NOW(), 1),
        (2150, 'API 管理', 'SysApi', 1, 1, 'sys:api:list', 1, 1, 1, 21, NOW(), 1),
        (2160, '字典管理', 'SysDict', 1, 1, 'sys:dict:list', 1, 1, 1, 21, NOW(), 1),
        (2161, '字典查询', 'DictQuery', 1, 1, 'sys:dict:query', 1, 1, 1, 2160, NOW(), 1),
        (2162, '字典新增', 'DictAdd', 1, 1, 'sys:dict:add', 1, 1, 1, 2160, NOW(), 1),
        (2163, '字典删除', 'DictDel', 1, 1, 'sys:dict:del', 1, 1, 1, 2160, NOW(), 1),
        (2164, '字典修改', 'DictEdit', 1, 1, 'sys:dict:edit', 1, 1, 1, 2160, NOW(), 1),
        (2211, 'Redis 监控', 'Redis', 1, 1, 'sys:monitor:redis', 1, 1, 1, 22, NOW(), 1),
        (2222, '服务器监控', 'Server', 1, 1, 'sys:monitor:server', 1, 1, 1, 22, NOW(), 1),
        (2311, '登录日志', 'Login', 1, 1, 'sys:login:list', 1, 1, 1, 23, NOW(), 1),
        (2322, '操作日志', 'Opera', 1, 1, 'sys:Opera:list', 1, 1, 1, 23, NOW(), 1)
        -- ############################## 商家端  ################################
        (3000, '工作台', 'Workplace', 0, 0, NULL, 1, 1, 1, NULL, NOW(), 0),
        (5000, '系统管理', 'System', 0, 0, NULL, 1, 1, 1, NULL, NOW(), 0),
        (5010, '部门管理', 'SysDept', 1, 1, 'sys:dept:list', 1, 1, 1, 3000, NOW(), 0),
        (5011, '部门查询', 'QueryDept', 2, 2, 'sys:dept:query', 1, 1, 1, 5010, NOW(), 0),
        (5012, '部门新增', 'AddDept', 2, 2, 'sys:dept:add', 1, 1, 1, 5010, NOW(), 0),
        (5014, '部门删除', 'DelDept', 2, 2, 'sys:dept:del', 1, 1, 1, 5010, NOW(), 0),
        (5015, '部门删除', 'UpdateDept', 2, 2, 'sys:dept:edit', 1, 1, 1, 5010, NOW(), 0),
        (5020, '用户管理', 'SysUser', 1, 1, 'sys:user:list', 1, 1, 1, 3000, NOW(), 0),
        (5021, '用户查询', 'QueryUser', 2, 2, 'sys:user:query', 1, 1, 1, 5020, NOW(), 0),
        (5022, '用户新增', 'AddUser', 2, 2, 'sys:user:add', 1, 1, 1, 5020, NOW(), 0),
        (5023, '用户删除', 'DelUser', 2, 2, 'sys:user:del', 1, 1, 1, 5020, NOW(), 0),
        (5024, '用户修改', 'UpdateUser', 2, 2, 'sys:user:edit', 1, 1, 1, 5020, NOW(), 0),
        (5030, '角色管理', 'SysRole', 1, 1, 'sys:role:list', 1, 1, 1, 3000, NOW(), 0),
        (5031, '角色查询', 'AueryRole', 2, 2, 'sys:role:query', 1, 1, 1, 5030, NOW(), 0),
        (5032, '角色新增', 'AddRole', 2, 2, 'sys:role:add', 1, 1, 1, 5030, NOW(), 0),
        (5033, '角色删除', 'DelRole', 2, 2, 'sys:role:del', 1, 1, 1, 5030, NOW(), 0),
        (5034, '角色修改', 'UpdateRole', 2, 2, 'sys:role:edit', 1, 1, 1, 5030, NOW(), 0),
        (5040, '菜单管理', 'SysMenu', 1, 1, 'sys:menu:list', 1, 1, 1, 3000, NOW(), 0),
        (5041, '菜单查询', 'QueryMenu', 2, 2, 'sys:menu:query', 1, 1, 1, 5040, NOW(), 0),
        (5042, '菜单新增', 'AddMenu', 2, 2, 'sys:menu:add', 1, 1, 1, 5040, NOW(), 0),
        (5043, '菜单删除', 'DelMenu', 2, 2, 'sys:menu:del', 1, 1, 1, 5040, NOW(), 0),
        (5044, '菜单修改', 'UpdateMenu', 2, 2, 'sys:menu:edit', 1, 1, 1, 5040, NOW(), 0)

insert into sys_role (id, name, status, remark, created_time, updated_time)
values  (1, 'test', 1, null, '2023-06-26 17:13:45', null);

insert into sys_role_menu (id, role_id, menu_id)
values  (1, 1, 1);

insert into sys_user (id, uuid, username, nickname, password, salt, email, is_superuser, is_staff, status, is_multi_login, avatar, phone, join_time, last_login_time, dept_id, created_time, updated_time)
values  (1, 'af4c804f-3966-4949-ace2-3bb7416ea926', 'admin', '用户88888', '$2b$12$8y2eNucX19VjmZ3tYhBLcOsBwy9w1IjBQE4SSqwMDL5bGQVp2wqS.', 0x24326224313224387932654E7563583139566A6D5A33745968424C634F, 'admin@example.com', 1, 1, 1, 0, null, null, '2023-06-26 17:13:45', '2024-11-18 13:53:57', 1, '2023-06-26 17:13:45', '2024-11-18 13:53:57');

insert into sys_user_role (id, user_id, role_id)
values  (1, 1, 1);
