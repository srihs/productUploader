from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.db import transaction
from django.http import JsonResponse
from django.template.loader import render_to_string
from decimal import *
import math


from .decorators import office_required
from .forms import CreateShipmentForm, CreateProductForm, CreateShipmentDetails, CreateCostFactorForm
from .models import Shipment, ProductTypes, ShipmentDetail, Country, Products

# global variables
shipment_list = None
shipmentItem_list = None
shipmentTotal = None
shipmentTotalQty = None
selectedShipment = None


########

# global Methods
# This function will accept a shipmentID and return a shipmentItemList


def getShipmentItemsList(shipmentId):
    if shipmentId is None:
        shipmentItem_list = None
    else:
        shipmentItem_list = ShipmentDetail.objects.filter(
            shipment=shipmentId, archived='0').select_related('product').select_related(
            'product__types')
    return shipmentItem_list

@login_required
def home(request):
    # clearing the session form the system. so the New id will be facilitated
    return render(request, '../templates/mainSection/home.html')


# This method will handle the create shipment request
@login_required
def createshipment(request):
    if request.method == "GET":

        # clearing the session form the system. so the New id will be facilitated
        request.session['shipmentID'] = None
        request.session.modified = True

        # shipmentNumber is defined by 'SHN-000' + next Id in the shipment Table
        try:
            # trying to retrive the next primaryKey
            nextId = Shipment.objects.all().count()
            nextId += 1
        except:
            # if the next ID is null define the record as the first
            nextId = 1
        shipmentPointList = Country.objects.all()
        # creating the form with the shipment ID
        form = CreateShipmentForm(
            initial={'shipmentNumber': 'SHN-000' + str(nextId)})

    return render(request, '../templates/mainSection/createshipment.html', {'form': form, 'user': request.user, 'shipmentPointList': shipmentPointList})


# This method will handle the Save shipment request
@login_required
def saveshipment(request):
    if request.method == 'POST':
        form = CreateShipmentForm(request.POST)
        if form.is_valid():
            objShipment = form.save(commit=False)
            objCountry = get_object_or_404(Country, pk=request.POST.get('shipmentPointDropDown'))

            objShipment.shippingPoint = objCountry
            objShipment.buyer = request.user
            objShipment.save()
        else:
            messages.error(request, form.errors)
        return redirect('mainSection:fillshipment')


@login_required
def viewshipment(request):
    # Retrieving The shipments which are open to fill.
    if request.user.is_officeUser or request.user.is_storeUser:
        shipment_list = Shipment.objects.all()
    else:
        shipment_list = Shipment.objects.filter(buyer=request.user)

    shipmentItem_list = None

    if request.method == 'GET':
        return render(request, '../templates/mainSection/viewshipment.html', {'shipments': shipment_list})

    if request.method == 'POST':
        # if the request if for a shipment that is selected in the dropdown the the following code block will execute
        if request.POST['shipmentDropDown']:

            # getting the shipmentID
            shipmentID = request.POST.get('shipmentDropDown')
            # Saving the selected Shipment object to passback to the template
            selectedShipment = Shipment.objects.select_related('shippingPoint').select_related('buyer').get(id=shipmentID)



            # getting the shipment List
            shipmentItem_list = getShipmentItemsList(shipmentID)
            shipmentTotal = 0
            shipmentTotalQty = 0
            shippingWeight = 0
            for shipment in shipmentItem_list:
                shipmentTotal += shipment.totalAmount
                shipmentTotalQty += shipment.qty
                shippingWeight += shipment.weight * shipment.qty

            shippingWeightKG = shippingWeight/1000

        else:
            messages.error(request, "Something went wrong.")

        return render(request, '../templates/mainSection/viewshipment.html',
                      {'shipments': shipment_list, 'shipmentDetails': shipmentItem_list, 'shipmentTotal': shipmentTotal,
                       'shipmentTotalQty': shipmentTotalQty, 'selectedShipment': selectedShipment,'shippingWeightKG':shippingWeightKG})


@login_required
@office_required
def reviewShipment(request):
    shipment_list = Shipment.objects.filter(isClosed='False', isFinalized='1', isCostbaseFinalized='1')

    if request.method == 'GET':
        if request.method == 'GET' and request.session['shipmentID'] is not None:
            shipmentID = request.session['shipmentID']
            # Saving the selected Shipment object to passback to the template
            # selectedShipment = get_object_or_404(Shipment, pk=shipmentID)
            selectedShipment = Shipment.objects.get(pk=shipmentID)

            shipmentItem_list = getShipmentItemsList(shipmentID)
            shipmentTotal = 0
            shipmentTotalQty = 0
            shippingWeight = 0

            for shipment in shipmentItem_list:
                shipmentTotal += shipment.totalAmount
                shipmentTotalQty += shipment.qty
                shippingWeight += shipment.weight * shipment.qty

            shippingWeightKG = shippingWeight / 1000

        else:
            print('here')
            request.session['shipmentID'] = None
            request.session.modified = True
            return render(request, '../templates/mainSection/reviewshipment.html', {'shipments': shipment_list})

    if request.method == 'POST':
        # if the request if for a shipment that is selected in the dropdown the the following code block will execute
        if request.POST.get('shipmentDropDown'):
            # getting the shipmentID and store it in sthe seesion
            shipmentID = request.POST.get('shipmentDropDown')
            request.session['shipmentID'] = shipmentID
            # Saving the selected Shipment object to passback to the template
            #selectedShipment = get_object_or_404(Shipment, pk=shipmentID)
            selectedShipment = Shipment.objects.get(pk=shipmentID)
            shipmentItem_list = getShipmentItemsList(shipmentID)
            shipmentTotal = 0
            shipmentTotalQty = 0
            shippingWeight = 0

            for shipment in shipmentItem_list:
                shipmentTotal += shipment.totalAmount
                shipmentTotalQty += shipment.qty
                shippingWeight += shipment.weight * shipment.qty

            shippingWeightKG = shippingWeight / 1000



    return render(request, '../templates/mainSection/reviewshipment.html',
                  {'shipments': shipment_list, 'shipmentDetails': shipmentItem_list, 'shipmentTotal': shipmentTotal,
                   'shipmentTotalQty': shipmentTotalQty, 'selectedShipment': selectedShipment ,'shippingWeightKG':shippingWeightKG})


# This method will handle the fillshipment request
@login_required
def fillshipment(request):
    # initializing objects
    productForm = CreateProductForm()
    shipmentDetailForm = CreateShipmentDetails()


    # Retrieving The Product types for the ShipmentForm
    productType_list = ProductTypes.objects.all()

    # Retrieving The shipments which are open to fill. Only loged in users orders will be listed.
    shipment_list = Shipment.objects.filter(
        isClosed='False', isFinalized='0', buyer=request.user)

    # if the request if for a shipment that is selected in the dropdown the the following code block will execute
    if request.GET.get('shipmentDropDown'):

        # getting the shipmentID
        shipmentID = request.GET.get('shipmentDropDown')

        # getting the shipment List
        shipmentItem_list = getShipmentItemsList(shipmentID)

        # Saving the selected Shipment object to passback to the template
        selectedShipment = get_object_or_404(Shipment, pk=shipmentID)

        # stroing the shipment Id for the save operation
        request.session['shipmentID'] = selectedShipment.id

    # This block will handel the requests with out shipping Id
    elif request.method == 'GET' and request is not None and 'shipmentID' in request.session and request.session['shipmentID'] is not None:
        shipmentItem_list = getShipmentItemsList(request.session['shipmentID'])
        # since the session.flush is voided due to the the authentication issue, ShipmentID is set to null in the
        # session variable therefor need to check for null.
        selectedShipment = Shipment.objects.get(
            id=request.session['shipmentID'])
    else:
        shipmentItem_list = None
        selectedShipment = None

    return render(request, '../templates/mainSection/fillshipment.html',
                  {'selectedShipment': selectedShipment, 'productTypes': productType_list, 'shipments': shipment_list,
                   'productForm': productForm, 'shipmentDetails': shipmentItem_list,
                   'ShipmentForm': shipmentDetailForm})


# This method will handle the save product request
@login_required
def saveproduct(request):
    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES)
        shipmentDetialForm = CreateShipmentDetails(request.POST)

        # loading the product type that was assigned to the product
        productType = get_object_or_404(
            ProductTypes, pk=request.POST['productType'])

        # loading the ShipmentID
        shipmentID = request.session['shipmentID']

        if form.is_valid() and shipmentDetialForm.is_valid():
            productObj = form.save(commit=False)

            # assigning the product Type
            productObj.types = productType

            # assigning the product image
            productObj.productImg = request.FILES['img']

            # productObj.productImage=file
            productObj.save()

            # creating the shipment detail Object
            shipmentDetailObj = shipmentDetialForm.save(commit=False)
            shipmentDetailObj.product = productObj
            shipmentDetailObj.weight = productObj.weight
            shipmentDetailObj.shipment = Shipment.objects.get(id=shipmentID)
            shipmentDetailObj.save()

        else:
            messages.error(request, form.errors)

        return redirect('mainSection:fillshipment')


# This method will handle the delete shipmentdetail request
@login_required
def deleteshipmentdetail(request, pk):
    objShipmentDetail = get_object_or_404(ShipmentDetail, pk=pk)
    if request.method == 'GET':
        # we are setting a parameter to mark the item as deleted.
        objShipmentDetail.archived = True
        objShipmentDetail.save()
    return redirect('mainSection:fillshipment')


# This method will handle the finalize shipment Request
@login_required
def finalizeshipment(request):
    if 'shipmentID' in request.session:
        objShipment = get_object_or_404(
            Shipment, pk=request.session['shipmentID'])

    if request.method == "POST":
        shipmentItem_list = getShipmentItemsList(objShipment.id)
        if shipmentItem_list.count() > 0:
            objShipment.isFinalized = True
            objShipment.save()
            # clearing the session form the system. so the New id will be facilitated
            request.session['shipmentID'] = None
            request.session.modified = True
        else:
            messages.error(
                request, 'This Shipment has no products assigned. Please add products before finalize the shipment.')

    return redirect('mainSection:fillshipment')


@login_required
@transaction.atomic
def generateCostFactor(request):
    # clearing the session form the system. so the New id will be facilitated


    shipment_list = None
    shipment_list = Shipment.objects.filter(isClosed='0', isFinalized='1', isCostbaseFinalized='False')
    form = CreateCostFactorForm()
    if request.method == 'GET':
        return render(request, '../templates/mainSection/costfactor.html', {'form': form, 'shipments': shipment_list})

    if request.method == 'POST':
            # if the request if for a shipment that is selected in the dropdown the the following code block will execute
            if request.POST.get('shipmentDropDown'):
                # getting the shipmentID
                shipmentID = request.POST.get('shipmentDropDown')
                request.session['shipmentID'] = shipmentID
                # Saving the selected Shipment object to passback to the template
                #selectedShipment = get_object_or_404(Shipment, pk=shipmentID)
                selectedShipment = Shipment.objects.get(pk=shipmentID)

                shipmentItem_list = getShipmentItemsList(shipmentID)
                shipmentTotal = 0
                shipmentTotalQty = 0
                shippingWeight=0

                for shipment in shipmentItem_list:
                    shipmentTotal += shipment.totalAmount
                    shipmentTotalQty += shipment.qty
                    shippingWeight += shipment.weight * shipment.qty

                shippingWeightKG = shippingWeight / 1000

            else:
                form = CreateCostFactorForm(request.POST, request.FILES)
                if form.is_valid():
                    shipmnetID = request.session['shipmentID']
                    objShipment = get_object_or_404(Shipment, pk=request.session['shipmentID'])
                    objShipment.isCostbaseFinalized = True
                    objShipment.costBase = form.cleaned_data['costBase']
                    # assigning the cost file
                    objShipment.costFile = form.cleaned_data['costFile']

                    shipmentItem_list = getShipmentItemsList(shipmnetID)

                    for shipmentItem in shipmentItem_list:
                        shipmentItem.costBase = objShipment.costBase
                        shipmentItem.save()

                    objShipment.save()
                    form = CreateCostFactorForm()  # Added this to clear the previous values for fields
                    return render(request, '../templates/mainSection/costfactor.html',
                                  {'form': form, 'shipments': shipment_list})
                    messages.success(request, "Cost base updated for the Shipment. Please verify the Shipment.")
                    # clearing the session form the system. so the New id will be facilitated
                    request.session['shipmentID'] = None
                    request.session.modified = True

                else:
                        messages.error(request, "Something went wrong.")

                # clearing the session form the system. so the New id will be facilitated


    return render(request, '../templates/mainSection/costfactor.html',
                  {'form': form, 'shipments': shipment_list,'shipmentTotal': shipmentTotal,
                   'shipmentTotalQty': shipmentTotalQty, 'selectedShipment': selectedShipment,'shippingWeightKG':shippingWeightKG})


@transaction.atomic
@login_required
@office_required
def updateproduct(request, pk):
    data = dict()

    if request.method == 'POST':
        objShipmentDetail = ShipmentDetail.objects.get(pk=pk)

        if objShipmentDetail is not None:
            objShipmentDetail.sellingPrice = request.POST['sellingPrice']
            if Decimal(objShipmentDetail.cost) > Decimal(objShipmentDetail.sellingPrice):
                messages.error(request, "Cost for the item is  Rs." + str(round(objShipmentDetail.cost,2)) +" . You have entered a price less than the cost.")
            else:
                objShipmentDetail.is_checked = True
                # productObj.productImage=file
                objShipmentDetail.save()
                objProject = Products.objects.get(pk=objShipmentDetail.product.id)
                objProject.sellingPrice = request.POST['sellingPrice']
                objProject.save()

    else:
        print('GET')
        objShipmentDetail = ShipmentDetail.objects.get(pk=pk)
        print(objShipmentDetail)
        form = CreateShipmentDetails(instance=objShipmentDetail)
        context = {'form': form}
        data['html_form'] = render_to_string('../templates/mainSection/partials/editproduct.html', context, request=request)
        return JsonResponse(data)

    return redirect('mainSection:reviewshipment')


def closeshipment(request):
    if request.method == 'POST':
        shipmentItem_list = ShipmentDetail.objects.filter(shipment=request.session['shipmentID'], archived='0',is_checked='0')
        if shipmentItem_list.count() > 0 :
            messages.error(request, "There are " + str(shipmentItem_list.count()) + " item(s) that need to be review. Please make sure all the items are reviewed. ")
        else:
            objShipment = Shipment.objects.get(pk=request.session['shipmentID'])
            objShipment.isClosed = True
            objShipment.save()
            # clearing the session form the system. so the New id will be facilitated
            request.session['shipmentID'] = None
            request.session.modified = True
            messages.success(request, messages.INFO, "Shipment " + objShipment.shipmentNumber +  " Closed")

    return redirect('mainSection:reviewshipment')




