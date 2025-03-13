workspace {
    name "leadertask"
    description "leadertask - приложение для планирования задач"

    !identifiers hierarchical

    model {
        user = person "Пользователь" 

        task_system = softwareSystem "leadertask" {

            group "Хранение данных" {
                goal_db = container "Goal Database" {
                    description "Хранение данных о целях" 
                    technology "PostgreSQL"
                    tags "database"
                }
                
                user_db = container "User Database" {
                    description "Хранение данных о пользователях" 
                    technology "PostgreSQL"
                    tags "database"
                }

                task_db = container "Task Database" {
                    description "Хранение данных о задачах" 
                    technology "PostgreSQL"
                    tags "database"
                    -> goal_db "Привязка задач к целям" "PostqreSQL"
                }
            }

            user_service = container "User Service" {
                description "Реализует обработку запросов, относящихся к пользователю"
                technology "С++"
            }
            task_service = container "Task Service" {
                description "Реализует обработку запросов, относящихся к задачам"
                technology "С++"
                -> task_db "Хранение и получение информации о задачах"
            }
            goal_service = container "Goal Service" {
                description "Реализует обработку запросов, относящихся к целям"
                technology "С++"
                -> goal_db "Хранение и получение информации о целях"
            }
        }
        user -> task_system.user_service "Взаимодействует для получения списка целей и задач"
        
        task_system.user_service -> task_system.user_db "Хранение и чтение данных о пользователях"
        task_system.user_service -> task_system.goal_service "Запрос на получение информации о целях"
        task_system.user_service -> task_system.task_service "Запрос на получение информации о задачах"
    }



    views {

        themes default
        styles {
            element "database" {
                shape cylinder
            }
        }

        systemContext task_system "Context" {
            include *
            autoLayout lr
        }
        
        container task_system "Container" {
            include *
            autoLayout lr
        }

        dynamic task_system "uc01" "Создание нового пользователя" {
            autoLayout
            user -> task_system.user_service "Создание нового пользователя (POST /user)"
            task_system.user_service -> task_system.user_db "Создает запись о пользователе в базе данных" 
        }

        dynamic task_system "uc02" "Поиск пользователя по логину" {
            autoLayout
            user -> task_system.user_service "Поиск пользователя по логину (GET /user?login={login})"
            task_system.user_service -> task_system.user_db "Получает данные о пользователе по логину"
        }

        dynamic task_system "uc03" "Поиск пользователя по маске имя и фамилии" {
            autoLayout
            user -> task_system.user_service "Поиск пользователя по имени и фамилии (GET /user?name={name}&surname={surname})"
            task_system.user_service -> task_system.user_db "Получает данные о пользователе по имени и фамилии"
        }

        dynamic task_system "uc04" "Создание новой цели" {
            autoLayout
            user -> task_system.user_service "Создание новой цели (POST /goal)"
            task_system.user_service -> task_system.goal_service "Передача данных о новой цели"
            task_system.goal_service -> task_system.goal_db "Создает запись в базе данных (INSERT INTO goals)"
        }

        dynamic task_system "uc05" "Получение списка всех целей" {
            autoLayout
            user -> task_system.user_service "Запрашивает список всех целей (GET /goals)"
            task_system.user_service -> task_system.goal_service "Передача запроса для поиска списка всех целей"
            task_system.goal_service -> task_system.goal_db "Возвращает список целей (SELECT * FROM goals)"
        }

        dynamic task_system "uc06" "Создание новой задачи на пути к цели" {
            autoLayout
            user -> task_system.user_service "Создание новой задачи (POST /task)"
            task_system.user_service -> task_system.task_service "Передача данных о новой задачи"
            task_system.task_service -> task_system.task_db "INSERT INTO tasks"
            task_system.task_db -> task_system.goal_db "Привязка новой задачи к цели"
        }

        dynamic task_system "uc07" "Получение всех задач цели" {
            autoLayout
            user -> task_system.user_service "Запрашивает список задач (GET /tasks)"
            task_system.user_service -> task_system.task_service "Передает запрос на получение списка задач"
            task_system.task_service -> task_system.task_db "Возвращает список задач"
        }

        dynamic task_system "uc08" "Изменение статуса задачи в цели" {
            autoLayout
            user -> task_system.user_service "Поиск и изменение задачи в нужной цели (GET /task?goal_id={goal_id})"
            task_system.user_service -> task_system.task_service "Передает запрос на получение задачи, привязанной к цели"
            task_system.task_service -> task_system.task_db "Возвращает задачу, привязанную к цели (INSERT INTO tasks WHERE goal_id={goal_id})"
        }
    }

}
