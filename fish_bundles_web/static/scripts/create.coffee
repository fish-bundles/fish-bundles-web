markdownTemplate = """
Introduction
------------

This bundle does something cool.

Usage
-----

install with fish-bundles by adding to your `fish-bundles-list.fish` file:

    set -gx _fish_bundles_list $_fish_bundles_list '<user>/<bundle-name>'

Provided Functions
------------------

This bundle comes with the following functions:

* does-something-nice - does something nice with the given $argv
* does-other-thing - otherify the thingy in the filesystem
"""

bundleMainTemplate = """
function my-function
    echo Hello $argv
end
"""

class CreateCtrl
    constructor: (@element) ->
        @selectedRepository = null
        @createDataTables()
        @bindEvents()

    createDataTables: ->
        @tbl = @element.find('#tbl-repositories')
        @tbl.dataTable
            "info":     false

        @tbl.on('click', 'tr', (ev) =>
            @tbl.$('tr.selected').removeClass('selected')
            row = $(ev.currentTarget)
            row.addClass('selected')
            @selectedRepository = row.attr('data-selected-id')
        )

    bindEvents: ->
        @elements =
            category: @element.find('#bundle-category')
            warning: @element.find('#duplicate-name')
            noRepo: @element.find('#no-repo')

        @element.find('.create-bundle-button').bind('click', (ev) =>
            obj =
                repository: @selectedRepository
                category: @elements.category.val()

            @createNewBundle(obj)
        )

    createNewBundle: (obj) ->
        @elements.warning.hide()

        if not @selectedRepository?
            @elements.noRepo.show()
            @elements.noRepo.fadeIn()
            return

        @elements.noRepo.hide()

        $.ajax({
            type: "POST",
            url: '/save-bundle',
            data:
                obj: JSON.stringify(obj),
            success: (result) =>
                resultObj = JSON.parse(result)
                if resultObj.result == 'duplicate_name'
                    @elements.warning.fadeIn()
                    return

                window.location = "/bundles/#{ resultObj.slug }"
        });


ctrl = new CreateCtrl($('.create-bundle'))
