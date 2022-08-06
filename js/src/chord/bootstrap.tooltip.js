/* ========================================================================
 * Bootstrap: tooltip.js v3.1.1
 * http://getbootstrap.com/javascript/#tooltip
 * Inspired by the original jQuery.tipsy by Jason Frame
 * ========================================================================
 * Copyright 2011-2014 Twitter, Inc.
 * Licensed under MIT (https://github.com/twbs/bootstrap/blob/master/LICENSE)
 * ======================================================================== */

export function tooltip($) {
    'use strict';

    // TOOLTIP PUBLIC CLASS DEFINITION
    // ===============================

    var Tooltip = function (element, options) {
        this.type       =
            this.options    =
                this.enabled    =
                    this.timeout    =
                        this.hoverState =
                            this.$measure   =
                                this.$element   = null

        this.init('tooltip', element, options)
    }

    Tooltip.DEFAULTS = {
        animation: true,
        mouseOffset: 0,
        measure: false,
        followMouse: false,
        placement: 'top',
        selector: false,
        template: '<div class="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>',
        trigger: 'hover focus',
        title: '',
        delay: 0,
        html: false,
        container: false
    }

    Tooltip.prototype.init = function (type, element, options) {
        this.enabled  = true
        this.type     = type
        this.$element = $(element)
        this.options  = this.getOptions(options)

        if (this.options.measure) {
            this.$measure = $(this.options.measure)
        }

        var triggers = this.options.trigger.split(' ')

        for (var i = triggers.length; i--;) {
            var trigger = triggers[i]

            if (trigger == 'click') {
                this.$element.on('click.' + this.type, this.options.selector, $.proxy(this.toggle, this))
            } else if (trigger != 'manual') {
                var eventIn  = trigger == 'hover' ? 'mouseenter' : 'focusin'
                var eventOut = trigger == 'hover' ? 'mouseleave' : 'focusout'

                this.$element.on(eventIn  + '.' + this.type, this.options.selector, $.proxy(this.enter, this))
                this.$element.on(eventOut + '.' + this.type, this.options.selector, $.proxy(this.leave, this))
            }
        }

        this.options.selector ?
            (this._options = $.extend({}, this.options, { trigger: 'manual', selector: '' })) :
            this.fixTitle()
    }

    Tooltip.prototype.getDefaults = function () {
        return Tooltip.DEFAULTS
    }

    Tooltip.prototype.getOptions = function (options) {
        options = $.extend({}, this.getDefaults(), this.$element.data(), options)

        if (options.delay && typeof options.delay == 'number') {
            options.delay = {
                show: options.delay,
                hide: options.delay
            }
        }

        return options
    }

    Tooltip.prototype.getDelegateOptions = function () {
        var options  = {}
        var defaults = this.getDefaults()

        this._options && $.each(this._options, function (key, value) {
            if (defaults[key] != value) options[key] = value
        })

        return options
    }

    Tooltip.prototype.enter = function (obj) {
        var self = obj instanceof this.constructor ?
            obj : $(obj.currentTarget)[this.type](this.getDelegateOptions()).data('bs.' + this.type)

        clearTimeout(self.timeout)

        self.hoverState = 'in'

        if (!self.options.delay || !self.options.delay.show) return self.show()

        self.timeout = setTimeout(function () {
            if (self.hoverState == 'in') self.show()
        }, self.options.delay.show)
    }

    Tooltip.prototype.leave = function (obj) {
        var self = obj instanceof this.constructor ?
            obj : $(obj.currentTarget)[this.type](this.getDelegateOptions()).data('bs.' + this.type)

        clearTimeout(self.timeout)

        self.hoverState = 'out'

        if (!self.options.delay || !self.options.delay.hide) return self.hide()

        self.timeout = setTimeout(function () {
            if (self.hoverState == 'out') self.hide()
        }, self.options.delay.hide)
    }

    Tooltip.prototype.show = function () {
        var e = $.Event('show.bs.' + this.type)

        if (this.hasContent() && this.enabled) {
            this.$element.trigger(e)

            if (e.isDefaultPrevented()) return
            var that = this;

            var $tip = this.tip()

            this.setContent()

            if (this.options.animation) $tip.addClass('fade')

            var placement = typeof this.options.placement == 'function' ?
                this.options.placement.call(this, $tip[0], this.$element[0]) :
                this.options.placement

            var autoToken = /\s?auto?\s?/i
            var autoPlace = autoToken.test(placement)
            if (autoPlace) placement = placement.replace(autoToken, '') || 'top'

            $tip
                .detach()
                .css({ top: 0, left: 0, display: 'block' })
                .addClass(placement)

            this.options.container ? $tip.appendTo(this.options.container) : $tip.insertAfter(this.$element)

            var pos          = this.getPosition()
            var actualWidth  = $tip[0].offsetWidth
            var actualHeight = $tip[0].offsetHeight

            if (autoPlace) {
                placement = this.getAutoPlace($tip, placement, pos, actualWidth, actualHeight)
            }

            var calculatedOffset = this.getCalculatedOffset(placement, pos, actualWidth, actualHeight)

            this.applyPlacement(calculatedOffset, placement)
            this.hoverState = null

            var complete = function() {
                that.$element.trigger('shown.bs.' + that.type)
            }

            if (this.options.followMouse) {
                $(this.options.container).on('mousemove', $.proxy(this.follow, this));
            }

            $.support.transition && this.$tip.hasClass('fade') ?
                $tip
                    .one($.support.transition.end, complete)
                    .emulateTransitionEnd(150) :
                complete()
        }
    }

    Tooltip.prototype.getAutoPlace = function($tip, placement, pos, actualWidth, actualHeight) {

        var $parent = this.$element.parent()

        var orgPlacement = placement
        var docScroll    = document.documentElement.scrollTop || document.body.scrollTop
        var parentWidth  = this.options.container == 'body' ? window.innerWidth  : $parent.outerWidth()
        var parentHeight = this.options.container == 'body' ? window.innerHeight : $parent.outerHeight()
        var parentLeft   = this.options.container == 'body' ? 0 : $parent.offset().left

        placement = placement == 'bottom' && pos.top   + pos.height  + actualHeight - docScroll > parentHeight  ? 'top'    :
            placement == 'top'    && pos.top   - docScroll   - actualHeight < 0                         ? 'bottom' :
                placement == 'right'  && pos.left  + actualWidth > parentWidth                              ? 'left'   :
                    placement == 'left'   && pos.left  - actualWidth < parentLeft                               ? 'right'  :
                        placement

        $tip
            .removeClass(orgPlacement)
            .addClass(placement)

        return placement
    }

    Tooltip.prototype.follow = function(e) {

        var $tip = this.tip()

        var pos          = this.getPosition()
        var actualWidth  = $tip[0].offsetWidth
        var actualHeight = $tip[0].offsetHeight

        var placement = typeof this.options.placement == 'function' ?
            this.options.placement.call(this, $tip[0], this.$element[0]) :
            this.options.placement

        var autoToken = /\s?auto?\s?/i
        var autoPlace = autoToken.test(placement)
        if (autoPlace) placement = placement.replace(autoToken, '') || 'top'

        pos.left = e.pageX + this.options.mouseOffset;
        pos.top = e.pageY + this.options.mouseOffset;

        var placement = this.getAutoPlace($tip, placement, pos, actualWidth, actualHeight)
        var calculatedOffset = this.getCalculatedOffset(placement, pos, actualWidth, actualHeight, e)

        this.applyPlacement(calculatedOffset, placement)
    }

    Tooltip.prototype.applyPlacement = function (offset, placement) {
        var replace
        var $tip   = this.tip()
        var width  = $tip[0].offsetWidth
        var height = $tip[0].offsetHeight

        // manually read margins because getBoundingClientRect includes difference
        var marginTop = parseInt($tip.css('margin-top'), 10)
        var marginLeft = parseInt($tip.css('margin-left'), 10)

        // we must check for NaN for ie 8/9
        if (isNaN(marginTop))  marginTop  = 0
        if (isNaN(marginLeft)) marginLeft = 0

        offset.top  = offset.top  + marginTop
        offset.left = offset.left + marginLeft

        // $.fn.offset doesn't round pixel values
        // so we use setOffset directly with our own function B-0
        $.offset.setOffset($tip[0], $.extend({
            using: function (props) {
                $tip.css({
                    top: Math.round(props.top),
                    left: Math.round(props.left)
                })
            }
        }, offset), 0)

        $tip.addClass('in')

        // check to see if placing tip in new offset caused the tip to resize itself
        var actualWidth  = $tip[0].offsetWidth
        var actualHeight = $tip[0].offsetHeight

        if (placement == 'top' && actualHeight != height) {
            replace = true
            offset.top = offset.top + height - actualHeight
        }

        if (/bottom|top/.test(placement)) {
            var delta = 0

            if (offset.left < 0) {
                delta       = offset.left * -2
                offset.left = 0

                $tip.offset(offset)

                actualWidth  = $tip[0].offsetWidth
                actualHeight = $tip[0].offsetHeight
            }

            this.replaceArrow(delta - width + actualWidth, actualWidth, 'left')
        } else {
            this.replaceArrow(actualHeight - height, actualHeight, 'top')
        }

        if (replace) $tip.offset(offset)
    }

    Tooltip.prototype.replaceArrow = function (delta, dimension, position) {

        if(this.options.mouseOffset > 0 && position === 'top') {
            this.arrow().css(position, this.options.mouseOffset + 10 + 'px')
            return;
        }

        this.arrow().css(position, delta ? (50 * (1 - delta / dimension) + '%') : '')
    }

    Tooltip.prototype.setContent = function () {
        var $tip  = this.tip()
        var title = this.getTitle()

        $tip.find('.tooltip-inner')[this.options.html ? 'html' : 'text'](title)
        $tip.removeClass('fade in top bottom left right')
    }

    Tooltip.prototype.hide = function () {
        var that = this
        var $tip = this.tip()
        var e    = $.Event('hide.bs.' + this.type)

        function complete() {
            if (that.hoverState != 'in') $tip.detach()
            that.$element.trigger('hidden.bs.' + that.type)
        }

        $(this.options.container).off('mousemove');
        this.$element.trigger(e)

        if (e.isDefaultPrevented()) return

        $tip.removeClass('in')

        $.support.transition && this.$tip.hasClass('fade') ?
            $tip
                .one($.support.transition.end, complete)
                .emulateTransitionEnd(150) :
            complete()

        this.hoverState = null

        return this
    }

    Tooltip.prototype.fixTitle = function () {
        var $e = this.$element
        if ($e.attr('title') || typeof($e.attr('data-original-title')) != 'string') {
            $e.attr('data-original-title', $e.attr('title') || '').attr('title', '')
        }
    }

    Tooltip.prototype.hasContent = function () {
        return this.getTitle()
    }

    Tooltip.prototype.getPosition = function () {

        var el = this.$element[0]
        if(this.$element.prop('tagName') == 'AREA') {

            var position = this.$element.attr('coords').split(',');
            var x = parseInt(position[0], 0) + parseInt(this.$measure.offset().left, 0);
            var y = parseInt(position[1], 0) + parseInt(this.$measure.offset().top, 0);

            return {bottom: 0, height: el.offsetWidth, left: x, right: 0, top: y, width: el.offsetWidth}
        }

        return $.extend({}, (typeof el.getBoundingClientRect == 'function') ? el.getBoundingClientRect() : {
            width: el.offsetWidth,
            height: el.offsetHeight
        }, this.$element.offset())
    }

    Tooltip.prototype.getCalculatedOffset = function (placement, pos, actualWidth, actualHeight, follow) {

        if (typeof follow !== 'undefined') {

            return  placement == 'bottom' ? { top: follow.pageY + this.options.mouseOffset, left: follow.pageX - (actualWidth / 2)  } :
                placement == 'top'    ? { top: follow.pageY - actualHeight - this.options.mouseOffset, left: follow.pageX - (actualWidth / 2)  } :
                    placement == 'left'   ? { top: follow.pageY - this.options.mouseOffset, left: follow.pageX - (actualWidth + this.options.mouseOffset) } :
                        { top: follow.pageY - this.options.mouseOffset, left: follow.pageX + this.options.mouseOffset }
        }

        return placement == 'bottom' ? { top: pos.top + pos.height,   left: pos.left + pos.width / 2 - actualWidth / 2  } :
            placement == 'top'    ? { top: pos.top - actualHeight, left: pos.left + pos.width / 2 - actualWidth / 2  } :
                placement == 'left'   ? { top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left - actualWidth } :
                    { top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left + pos.width   }
    }

    Tooltip.prototype.getTitle = function () {
        var title
        var $e = this.$element
        var o  = this.options

        title = $e.attr('data-original-title')
            || (typeof o.title == 'function' ? o.title.call($e[0]) :  o.title)

        return title
    }

    Tooltip.prototype.tip = function () {
        return this.$tip = this.$tip || $(this.options.template)
    }

    Tooltip.prototype.arrow = function () {
        return this.$arrow = this.$arrow || this.tip().find('.tooltip-arrow')
    }

    Tooltip.prototype.validate = function () {
        if (!this.$element[0].parentNode) {
            this.hide()
            this.$element = null
            this.options  = null
        }
    }

    Tooltip.prototype.enable = function () {
        this.enabled = true
    }

    Tooltip.prototype.disable = function () {
        this.enabled = false
    }

    Tooltip.prototype.toggleEnabled = function () {
        this.enabled = !this.enabled
    }

    Tooltip.prototype.toggle = function (e) {
        var self = e ? $(e.currentTarget)[this.type](this.getDelegateOptions()).data('bs.' + this.type) : this
        self.tip().hasClass('in') ? self.leave(self) : self.enter(self)
    }

    Tooltip.prototype.destroy = function () {
        clearTimeout(this.timeout)
        this.hide().$element.off('.' + this.type).removeData('bs.' + this.type)
    }


    // TOOLTIP PLUGIN DEFINITION
    // =========================

    var old = $.fn.tooltip

    $.fn.tooltip = function (option) {
        return this.each(function () {
            var $this   = $(this)
            var data    = $this.data('bs.tooltip')
            var options = typeof option == 'object' && option

            if (!data && option == 'destroy') return
            if (!data) $this.data('bs.tooltip', (data = new Tooltip(this, options)))
            if (typeof option == 'string') data[option]()
        })
    }

    $.fn.tooltip.Constructor = Tooltip


    // TOOLTIP NO CONFLICT
    // ===================

    $.fn.tooltip.noConflict = function () {
        $.fn.tooltip = old
        return this
    }

}(jQuery);
