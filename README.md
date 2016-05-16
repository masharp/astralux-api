#Astralux API
Astralux REST API for the [Astralux Marketplace](https://github.com/masharp/astralux)
marketplace.  

Contact: michael@softwareontheshore.com
Follow Me: [@sharp_mi]('https://www.twitter.com/sharp_mi')

Technologies:
  * Python2
  * Flask
  * Heroku
  * PostgreSQL  

PostgreSQL Models:
  * Moonlet:
    * id: int, primary key
    * name: string
    * description: string
    * type: string
    * inventory: int
    * price: float
    * limited: boolean
    * discount: float
    * img_src: string
