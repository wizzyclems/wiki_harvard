from random import Random, randrange
import random
from django.shortcuts import render
from django import forms
import markdown2
from . import util
from django.http import HttpResponseRedirect
from django.urls import reverse

class NewWikiForm(forms.Form):
    title = forms.CharField(label="Title:",min_length=2, widget=forms.TextInput)
    markdown = forms.CharField(label="Mark Down",widget=forms.Textarea(attrs={'cols': 5,'rows':3}))
    #priority = forms.IntegerField(label="Priority", min_value=1, max_value=5)

    def clean_title(self):
        title = self.cleaned_data.get("title")
        
        if util.get_entry(title) != None :
            msg = 'The specified title already exists.'
            raise forms.ValidationError(msg)

        return title



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def search(request):
    print("This is the search view...")
    search = request.GET.get('q')
    if search : 
        wiki_content = util.get_entry(search)

        if wiki_content == None :
            subs_search = []
            all_wikis = util.list_entries()
            for wiki in all_wikis :
                if search.lower() in wiki.lower():
                    subs_search.append(wiki)

            return render(request, "encyclopedia/search.html", {
                "entries": subs_search
            } )

        else:
            wiki_content = markdown2.markdown(wiki_content)

            return render(request, "encyclopedia/wiki.html", {
                "title": search.upper() ,
                "content": wiki_content
            } )

    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })

def randomPage(request):
    all_wikis = util.list_entries()
    
    randWiki = randrange(0, len(all_wikis)-1 )
    title = all_wikis[randWiki]
    wiki_content = markdown2.markdown( util.get_entry(title) )

    return render(request, "encyclopedia/wiki.html", {
        "title": title,
        "content": wiki_content
    })


def edit(request, title):
    print("There is an attempt to edit a page {}".format(title))

    if request.method == 'POST': # The below lines of code are executed if a POST request was made to edit. This means a form submission to us.
        wikiForm = NewWikiForm(request.POST)
        markdown = request.POST["markdown"]

        if title == "New Wiki": #If the place holder title "New Wiki" was returned, it means it is an attempt to create a new wiki
            if wikiForm.is_valid():
                wikiForm.cleaned_data["title"] = request.POST["title"]
                title = wikiForm.cleaned_data["title"]
                markdown = wikiForm.cleaned_data["markdown"]
                print("creating with a title of  {}".format(title))
            else:
                print("The form is not valid")
                return renderWikiForm(request,title,wikiForm)
        else:
            #This line ensures a user does not change the title of a wiki while trying to edit it. Only markdowns can be edited.
            newTitle = request.POST["title"] 
            if title.lower() != newTitle.lower():
                wikiForm.add_error('title','You cannot edit the title of a wiki.')
                #title = wikiForm.cleaned_data["title"]
                markdown = wikiForm.cleaned_data["markdown"]
                return renderWikiForm(request, title,wikiForm)

            
            title = request.POST["title"]
            markdown = request.POST["markdown"]


        util.save_entry(title,markdown)
        return HttpResponseRedirect(reverse("wiki",kwargs={"title":title}))
        
    else:    # The below lines of code are executed if a GET request was made to edit. e.g User clicks the edit wiki button, or the create wiki link is clicked.
        wiki_content = util.get_entry(title)
        if wiki_content == None : #if title is None, it means user wants to create a new wiki
            title = "New Wiki"  #We assign this title placeholder as a way of distinguishing create wiki requests from edit requests
            wikiForm = NewWikiForm()
        else:   #if title is not None, it means users wants to edit an existing wiki
            wikiForm = NewWikiForm(initial={'title':title, 'markdown':wiki_content})
            #wikiForm.declared_fields['title'].disabled = True
       

    return renderWikiForm(request,title,wikiForm)


def renderWikiForm(request,title, wikiForm):
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "wikiForm": wikiForm
    })
    
def create(request):
    return edit(request, "")


def wiki(request, title):
    print(f"wiki page was called with title {title}")
    wiki_content = util.get_entry(title)
    error = False

    if wiki_content == None :
        error = True
        wiki_content = "<b style='color:red'>The requested page does not exist!</b>"
    else:
        wiki_content = markdown2.markdown(wiki_content)


    return render(request, "encyclopedia/wiki.html", {
        "title": title.upper() ,
        "content": wiki_content,
        "error": error
    } )


