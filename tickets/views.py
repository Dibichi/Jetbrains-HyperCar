from django.views import View
from django.http.response import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.conf import settings

# The welcome menu
class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')

# The main menu which links to all other menus
class MenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/menu.html')


ticket_num = 0 # keeps track of what ticket num program is on

# Handles service request - assigns a ticket number to customer and tells wait time
def service(request, service):

    # Calculates wait time based on recursion :)
    def calculate_wait(ticket):
        if ticket == 'change_oil':
            return (len(settings.QUEUE['change_oil'])) * 2
        elif ticket == 'inflate_tires':
            return calculate_wait('change_oil') + (len(settings.QUEUE['inflate_tires'])) * 5
        elif ticket == 'diagnostic':
            return calculate_wait('inflate_tires') + (len(settings.QUEUE['diagnostic'])) * 30

    global ticket_num
    ticket_num += 1
    wait_time = calculate_wait(service)
    settings.QUEUE[service].append(ticket_num) # updates queue
    context = {"name": service, "number": ticket_num, "wait": wait_time}
    return render(request, "tickets/tickets.html", context=context)

# Class responsible for handling workers
submitted = None
class ProcessingView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "tickets/process.html", context=settings.QUEUE)

    # Once submit button is pressed - the first ticket in line is set as submitted / processed
    def post(self, request, *args, **kwargs):
        for service in settings.QUEUE:
            if settings.QUEUE[service] != []:
                global submitted
                submitted = (settings.QUEUE[service])[0]
                (settings.QUEUE[service]).pop(0)
                break

        return redirect('/next/')

# Where customers can see who's ticket was just processed
class NextView(ProcessingView):
    def get(self, request, *args, **kwargs):
        global submitted
        context = {"Next": submitted} # the submitted ticket is seen on the 'next' page
        return render(request, "tickets/next.html", context=context)
