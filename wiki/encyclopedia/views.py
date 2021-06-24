from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms
from random import choice

import markdown2
import html

from . import util

class NewSearchForm(forms.Form):
    q = forms.CharField(widget=forms.TextInput(attrs = {'class': 'search',
                                                        'placeholder': 'Search Encyclopedia'}), 
                        label="",)

class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Page Title",
                                                          "autocomplete": "off",
                                                          "autofocus": ""}), 
                            label="")

    textArea = forms.CharField(widget=forms.Textarea(attrs={"class": "",
                                                            "placeholder": "Enter Markdown Content"}),
                               label="")

def index(request):
    if request.method == "POST":
        form = NewSearchForm(request.POST)
        if form.is_valid():
            # Get Query data and redirect user to correct entry
            search_entry = form.cleaned_data['q']

            # If query matches list of entries, redirect to entry page
            if util.get_entry(search_entry):
                return HttpResponseRedirect(f'/wiki/{search_entry.lower()}')

            # Else, send to search results page showing entries
            # that contain the substring of the query
            else:
                entry_matches = []
                entries = util.list_entries()
                for entry in entries:
                    if search_entry.lower() in entry.lower():
                        entry_matches.append(entry)
                
                # If query matches any of the entries, take them to search results
                if len(entry_matches) == 0:
                    return render(request, "encyclopedia/error.html")
                else:
                    return render(request, "encyclopedia/results.html", {
                        "query": search_entry.capitalize(),
                        "matches": entry_matches
                    })
    
    form = NewSearchForm()
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": form
    })

def entry(request, TITLE):
    entry = util.get_entry(TITLE)
    if not entry:
        return render(request, "encyclopedia/error.html")
    
    markdown_convert = markdown2.markdown(entry)

    return render(request, "encyclopedia/entry.html", {
            "title": str(TITLE).capitalize(),
            "entry": markdown_convert
        })

def edit(request):
    title = request.POST.get("title").strip()
    content = util.get_entry(title)

    # If submit changes button was clicked..
    if "submit" in request.POST:
        # Save changes to file by overwriting file w/ new entry
        entry_new = open(f"entries/{title.lower()}.md", "w")
        entry_new.write(content)
        entry_new.close()

        # Redirect user back to page
        return HttpResponseRedirect(f'/wiki/{title.lower()}')

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })

def create(request):
    if request.method == "POST":
        submitted_form = NewEntryForm(request.POST)
        if submitted_form.is_valid():
            newentry_title = submitted_form.cleaned_data["title"].strip().lower()

            # If encyclopedia entry already exists, present error message
            for entry in util.list_entries():
                if newentry_title == entry.lower():
                    return render(request, "encyclopedia/error.html")

            # Save entry to disk, and take user to new entry page
            entry_new = open(f"entries/{newentry_title.upper()}.md", "x")
            entry_content = submitted_form.cleaned_data["textArea"].strip()
            entry_new.write(entry_content)
            entry_new.close()

            return render(request, "encyclopedia/entry.html", {
                "title": newentry_title.capitalize(),
                "entry": util.get_entry(newentry_title)
            })

    form = NewEntryForm()
    return render(request, "encyclopedia/create.html", {
        "createpage_form": form
    })

def random(request):
    # Returns a random entry page
    entries = util.list_entries()
    random_entry = choice(entries)

    return render(request, "encyclopedia/entry.html", {
        "title": random_entry.capitalize(),
        "entry": util.get_entry(random_entry)
    })