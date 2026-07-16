def get_all_products():
    """
    List Available Products
    ---
    tags:
      - Products

    summary: Get all available subscription plans.

    description: |
      Returns the list of subscription plans
      available for purchase through Stripe.

    produces:
      - application/json

    responses:
      200:
        description: Products retrieved successfully.
        schema:
          type: object
          properties:
            products:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: Stripewise Starter
                  price:
                    type: integer
                    example: 999
                  tier:
                    type: string
                    enum:
                      - starter
                      - pro
                    example: starter
    """

    products = get_all_products()

    return {
        "products": products
    }, 200