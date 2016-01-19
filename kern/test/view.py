#
#  -*- coding: iso8859-1 -*-
#  /kern/test/view.py
#
from logica.views import (Presenter, View, ViewField, ViewGroup, ViewLayout, ViewModel,
    ButtonField, CheckboxField, HyperlinkField, LabelField, OneToMany, SelectField, TitleField)

        
class TestPresenter(Presenter):
    def __init__(self, *args, **kwargs):
        super(TestPresenter, self).__init__(*args, **kwargs)
        self.adressen = []
        for i in range(5):
            self.adressen += [("Naam %s" % i, "Adres %s" % i, "Woonplaats %s" % i)]

    def do_load_data(self):
        super(TestPresenter, self).do_load_data()
            
        testmodel = self._viewmodel
        testmodel.titel = "Een paar fake adressen"
        testmodel.adressen.clear()
        
        for (naam, adres, woonplaats) in self.adressen:
            adresmodel = AdresModel()
            adresmodel.naam = naam
            adresmodel.adres = adres
            adresmodel.woonplaats = woonplaats
            testmodel.adressen.append(adresmodel)

        for i in range(5):
            testmodel.dropdown[i+1] = "Keuze %d" % (i+1)

    def on_dialoog_knop_click(self, sender):
        resp = self.view.messagebox("Messagebox", "Dit is een voorbeeld van een messagebox.", View.DLG_YES_NO)
        self.view.messagebox("Antwoord", "U heeft '%s' gekozen." % (resp == View.CMD_YES and "ja" or "nee"))

    def on_dropdown_select(self, sender):
        self.view.messagebox("Selectie", "'%s:%s' geselecteerd." % (sender.items.selected, sender.items.value))

class TestView(View):
    def __init__(self, impl, presenter):
        View.__init__(self, impl, presenter)
                
    def update_view(self):
        super(TestView, self).update_view()

gr_knoppen = ViewGroup("knoppen", ViewLayout.HORIZONTAL)
gr_demo = ViewGroup("demo", ViewLayout.HORIZONTAL)

class AdresModel(ViewModel):
    verwijderen = CheckboxField(label="Verwijderen")
    naam = LabelField()
    adres = LabelField()
    woonplaats = LabelField()

class TestModel(ViewModel):
    titel = TitleField()
    adressen = OneToMany(AdresModel, group=ViewGroup("adressen", ViewLayout.FLEXGRID))
    dialoog_knop = ButtonField(group=gr_demo, label="Messagebox", value="messagebox")
    hyperlink = HyperlinkField(group=gr_demo, value="Hyperlink")
    dropdown = SelectField(group=gr_demo)
    ok_knop = ButtonField(group=gr_knoppen, label="OK", value=Presenter.ACTION_SAVE)
    update_knop = ButtonField(group=gr_knoppen, label="Update", value=Presenter.ACTION_UPDATE)
