# Zebrands Test

## Problem

### Description of the task

We need to build a basic catalog system to manage products. A product should have basic info such as sku, name, price and brand.

In this system, we need to have at least two type of users:

- admins to create / update / delete products and to create / update / delete other admins;
- anonymous users who can only retrieve products information but can't make changes.

As a special requirement, whenever an admin user makes a change in a product (for example, if a price is adjusted), we need to notify all other admins about the change, either via email or other mechanism.

We also need to keep track of the number of times every single product is queried by an anonymous user, so we can build some reports in the future.

Your task is to build this system implementing a REST or GraphQL API using the stack of your preference.

### If you want to stand out by going the extra mile, you could do some of the following:

- Add tests for your code
- Containerize the app
- Deploy the API to a real environment
- Use AWS SES or another 3rd party API to implement the notification system
- Provide API documentation (ideally, auto generated from code)
- Propose an architecture design and give an explanation about how it should scale in the future
- Delivering your solution

## Requirements

You need have Docker and Docker Compose installed in your system

Follow the steps for example in:
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04

## Clone repository

```sh
$ git clone https://github.com/eemanuel/
```

## Run docker-compose commands

```sh
$ docker-compose up
```

Go to the `zebrands_api_1` container's shell

```sh
$ docker exec -ti zebrands_api_1 bash
```

Inside the conteiner's shell, create the first user instance:

```sh
$ python manage.py createsuperuser
```

Here, you will enter your desired username and press enter key.
You will then be prompted for your desired email address.
The final step is to enter your password.

You can access to admin url only with this superuser.

## Install pre-commit locally

If you are develoeper you should install in you system:

```sh
pip install pre-commit
```

And at .git folder level execute:

```sh
pre-commit install
```

## Endpoints

### Admin

[GET] http://localhost:8000/admin/

### Check information about all endpoints:

[GET] http://localhost:8000/api_list

### Products

**Create:**
[POST] http://localhost:8000/products/

**List:**
[GET] http://localhost:8000/products/

**Retrieve:**
[GET] http://localhost:8000/products/<id>/

**Update:**
[PUT] http://localhost:8000/products/<id>/

**Patrial Updata:**
[PATCH] http://localhost:8000/products/<id>/

**Destroy:**
[DELETE] http://localhost:8000/products/<id>/

### Flower:

[GET] http://localhost:5555/
