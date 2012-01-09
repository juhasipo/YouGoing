/**
 * Check if Edited. Version 0.2
 * 
 * Monitors if an form has been changed.
 * Options:
 *  saveLink: Save link(s) to disable/enabled. jQuery selector or jQuery object. (Obligatory)
 *  saveLinkAction: Action to perform when save link is in enabled state and clicked. (Obligatory)
 *  linkDisabledClass: Class to set to save link(s) when it is disabled. (Optional) Default: "disabled"
 *  linkEnabledClass Class to set to save link(s) when it is enabled. (Optional) Default: "enabled"
 *  editField: Callback triggered when field has been edited. function(element) (Optional) Default: <do nothing>
 * @author MuZeR
 */
(function( $, undefined ) {
$.widget( "ui.checkIfEdited", {
	options: {
		saveLink: undefined,
		saveLinkAction: undefined,
		linkDisabledClass: "disabled",
		linkEnabledClass: "enabled",
		editField: undefined
	},
	
	isEdited: false,
	
	_create: function() {
		if( this.options.saveLinkAction == null || 
			this.options.saveLinkAction == undefined ) {
			alert("Option saveLinkAction must be defined!");
			return false;
		}
		if( !$.isFunction(this.options.saveLinkAction) ) {
			alert("Option saveLinkAction has to be a function!");
			return false;
		}
		
		if( typeof this.options.saveLink === "string" ) {
			this.options.saveLink = $(this.options.saveLink);
		}
		this._disableSaveLink();
		
		var self = this;
		$("input, select, textarea", this.element[0]).live('change', function(event) {
			self.isEdited = true;
			if( $.isFunction(self.options.editField) ) {
				self.options.editField($(this));
			}
			self._enableSaveLink();
		});
	},
	
	_disableSaveLink: function() {
		this.options.saveLink.addClass(this.options.linkDisabledClass);
		this.options.saveLink.removeClass(this.options.linkEnabledClass);
		this.options.saveLink.unbind('click');
	},
	_enableSaveLink: function() {
		this.options.saveLink.removeClass(this.options.linkDisabledClass);
		this.options.saveLink.addClass(this.options.linkEnabledClass);
		this.options.saveLink.click(this.options.saveLinkAction);
	},
	
	_destroy: function() {
		this.options.saveLink.unbind('click');
		this.options.saveLink.removeClass(this.options.linkDisabledClass);
		this.options.saveLink.addClass(this.options.linkDisabledClass);
		$("input, select, textarea", this.element[0]).die('change');
	},
});

})( jQuery );