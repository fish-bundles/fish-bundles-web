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
        @initializeCodeMirror()
        @bindEvents()

    initializeCodeMirror: ->
        extras =
            'F11': (cm) ->
                cm.setOption("fullScreen", !cm.getOption("fullScreen"))
            'Esc': (cm) ->
                cm.setOption("fullScreen", false) if cm.getOption("fullScreen")

        el = $('.plugin-main-fish', @element)[0]
        @mainMirror = @createCodeMirror(el, 'shell', extras, bundleMainTemplate)

        extras['Enter'] = 'newlineAndIndentContinueMarkdownList'
        el = $('.readme-md', @element)[0]
        @readmeMirror = @createCodeMirror(el, 'markdown', extras, markdownTemplate)

    createCodeMirror: (el, mode, extraKeys, value) ->
        CodeMirror(el,
            mode: mode,
            lineNumbers: true,
            theme: 'monokai',
            extraKeys: extraKeys,
            styleActiveLine: true,
            value: value
        )

    bindEvents: ->
        @elements =
            name: @element.find('#bundle-name')
            category: @element.find('#bundle-category')
            warning: @element.find('#duplicate-name')

        @element.find('.create-bundle-button').bind('click', (ev) =>
            obj =
                readme: @readmeMirror.getValue()
                main: @mainMirror.getValue()
                name: @elements.name.val()
                category: @elements.category.val()

            @createNewBundle(obj)
        )

    createNewBundle: (obj) ->
        @elements.warning.hide()

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
