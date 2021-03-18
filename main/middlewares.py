from . import models

def basket_middleware(get_response):
    def middleware(request):
        if 'basket_id' in request.session:
            basket_id = request.session['basket_id']
            basket = models.Basket.objects.get(id=basket_id)
            request.basket = basket
        else:
            request.basket=None
        response = get_response(request)
            
        return response
        
    return middleware

#class-based middlewares
class basket_middle:
    def __init__(self,get_response):
        self.get_response = get_response
    def __call__(self,request):
        self.request = request
        if 'basket_id' in self.request.session:
            basket_id = request.session['basket_id']
            basket = models.Basket.objects.get(id=basket_id)
            request.basket = basket
        else:
            request.basket = None
        self.response = self.get_response(request)
        return self.response


    