class HeaderCtrl
    constructor: (@element) ->
        @elements = {}
        @gatherElements()
        @bindEvents()

    gatherElements: ->
        @elements.installButton = $('.install-button')
        @elements.installInstructions = $('.install-instructions')
        @elements.mainContent = $('.main-content')

    bindEvents: ->
        @elements.installButton.on('click', (ev) =>
            @element.toggleClass('show-install')
            @elements.installInstructions.toggleClass('show')
            @elements.mainContent.toggleClass('show-install')
        )


header = new HeaderCtrl($('header'))
