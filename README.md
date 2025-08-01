# refbook-backend

**热书 Refbook** 后端服务器

## 项目结构

### 文件结构

- **module/**

    - **database/ ...** 数据库相关操作

    - **routes/ ...** API路由

    - **utils/ ...** 工具操作

- **app.py** 程序主入口

- Dockerfile ***Zeabur*** 服务器配置文件

---

### API结构

**api/**

- **user/ ...** 用户相关操作

    - **create/** 创建新用户

        方法: POST

        请求体:
        
        ```json
        {
            "username": "用户名",
            "password": "密码" // plain text password
        } 
        ```

        返回:

        ```json
        {
            "type": "success",
            // "message": "新用户的ID"
        }
        ```

        或

        ```json
        {
            "type": "failed",
            "message": "失败的原因"
        }
        ```

        > 创建后自行再次使用相同的username与password登录

    - **login/** 获取 _**OAuth2 token**_

        方法: POST

        请求体:

        ```json
        {
            "username": "用户名",
            "password_hash": "密码的加盐哈希"
        }
        ```

        返回值:

        ```json
        {
            "type": "failed",
            "message": "为什么失败"
        }
        ```

        或

        ```json
        {
            "type": "success",
            "message": "具体token"
        }
        ```

- **book/ ...** 书籍相关操作

    - ...

- **answer/** 问答相关操作

    - **create/** 创建一个问答
    
        方法: GET

        携带: Authorization Bearer \<token here\>

        返回值: 

        ```json
        {
            "type": "success",
            "message": "answer_id 一个新问答对话ID"
        }
        ```

        或

        ```json
        {
            "type": "failed",
            "message": "为什么失败"
        }
        ```

    - **ask/** 用户发送消息给AI 

        方法: POST

        携带: Authorization Bearer \<token here\>

        请求体:

        ```json
        {
            "message": "消息"
        }
        ```

        返回值: **无**

    - **answer/** 用户获取AI生成的信息

        方法: GET

        携带: Authorization Bearer \<token here\>

        返回值:

        ```json
        {
            "type": "success",
            "message": "AI生成的**信息delta** / **特定结束符** (maybe EOF or sth)"
        }
        ```

        或

        ```json
        {
            "type": "success",
            "message": "余额不够了 / **正在生成中**""
        }
        ```

- **chat_history/ ...** 用户聊天记录 相关操作

    - ...

---

### _Developed by **n1ghts4kura**_.
