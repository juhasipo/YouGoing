/**
 * 	 ToggleToEdit - Version 0.4
 * 
 * Adds possibility to toggle editing mode of selected input and select elements (fields)
 * via link. Creates <div class="immutable"> elements for each field which are
 * shown when the fields are not editable. Also sets the div id to "<field id>-immutable" if
 * the field has an ID.
 * Field specific options will override global options (e.g. showLabel for all fields vs. single field)
 *  Field option importance: Global option < id/name option < class
 *  N.B. If a field has two classes that are in fieldOptions, the behaviour is unpredicted. Therefore
 *  please use only one class to define fieldOptions
 * Options:
 *  linkElement: jQuery object or jQuery selector string for link which toggles element visibility
 *  uneditLinkElement: jQuery objecr or jQuery selector string for link which makes fields uneditable.
 *                     If this is defined, hideLinkAfterClick will hide linkElement and then show
 *                     this element. hideLinkAfterClick does not have any effect.
 *                     If this is not defined, hideLinkAfterClick defines linkElement behaviour.
 *  hideLinkAfterClick: Set to true if the edit link should be hidden after click (default: true)
 * 	isEditable: Set to true if elements should start as editable, false if not (default: false)
 *  showLabel: Shows label associated with input/select along with the uneditable field (default: true)
 *             Label has to have for attribute.
 *  markEmptyWithDash: Replace empty fields with dash when shown the uneditable fields (default: true)
 *  fieldOptionClassPrefix: Prefix for marking class field options. E.g. with the default prefix
                            .field-with-no-label is interpreted as class field option. (default: '.')
    copyClasses: Copy editable element classes to immutable
    ignoreElements: Ignore following elements
 *  fieldOptions: Additional options assigned for single fields.
 *                Key = field id, name or class, value = object containing field options
 *                   Id and name will override
 *                      showLabel: See global option
 *						checkboxesAsDisabled: See global option
 *						classes: "", Additional classes for uneditable field (div)
 *						markEmptyWithDash: See global option
 *						formatter: Function used for formatting field value. 
 *						            function(<field value as string>) : return <formatted value as string>
 *						createCallback: Called after element has been added to DOM and id and classes have been set. 
 *						                 function(<jQuery element>) : no return value
 *  checkboxesAsDisabled: Check boxes showed as disabled instead of true/false (default: true)
 *                        You can use formatter to localize the values shown if this is set false.
 * Depends:
 *   jquery.ui.core.js
 *   jquery.ui.widget.js
	 */
$.widget("ui.toggleToEdit", {
	// Default values for jQuery UI widget
	options: {
		immutables: [],
		linkElement: null,
		uneditLinkElement: null,
		isEditable: false,
		hideLinkAfterClick: false,
		checkboxes: [],
		elements: null,
		ignoreElements: null,
		hideableElements: null,
		showLabel: true,
		markEmptyWithDash: true,
		checkboxesAsDisabled: true,
		copyClasses: true,
		
		fieldOptions: {},
		fieldOptionClassPrefix: "."
	},
	classOptions: {},

	destroy: function() {
		this.showEditables();
		//this.options.immutables.remove(); //TODO
		$.Widget.prototype.destroy.call( this );
	},
	_create: function() {
		// Create necessary elements for each input/select
		var self = this;
		this._pickClassOptions(self);
		this.options.elements = this._findElements(this.element, this.options.ignoreElements);
		this.options.hideableElements = this._findHideableElements(this.element, this.options.hideableElements);
		this.options.elements.each(function(index, value) {
			var element = $(value);
			// Take the checkboxes into other array
			// because these will be disabled instead
			// of replacing them with new element
			var fieldNameOptions = self._findFieldOptions(element.attr('id'), element.attr('name'));
			var fieldClassOptions = self._findClassOptions(self,element);
			var fieldOptions = $().extend(true,{},fieldNameOptions,fieldClassOptions);
			if( element.is('input[type="hidden"]') ) {
				return;
			}
			if( self._isOptionTrue(fieldOptions, self.options, "checkboxesAsDisabled") && 
					element.is('input[type="checkbox"]')) {
				var elementValue = element.val();
				element.addClass("checkbox-as-disabled");
				self.options.checkboxes.push(element[0]);
				return;
			}
			// For other elements take the value which
			// represents the current state of the element
			else {
				var elementValue = self._getValueFromElement(element);
				if( $.isFunction(fieldOptions.formatter) ) {
					elementValue = fieldOptions.formatter(elementValue);
				}
			}

			// showLabel/hideLabelsWithFields
			var showLabel = self._isOptionTrue(fieldOptions, self.options, "showLabel");
			if( showLabel === false ) {
				var elementId = element.attr('id');
				var labelElement = $('label[for="' + elementId +'"]');
				if( elementId && labelElement.length > 0 ) {
					self.options.elements.push(labelElement[0]);
					labelElement.hide();
				}
			}
			
			element.hide();
			// Get classes from the original element so that
			// the new div elements can be styled with similar styles
			var elementClasses = "";
			if( self._isOptionTrue(fieldOptions, self.options, "copyClasses") ) {
			    elementClasses += element[0].className || "";
			}
			elementClasses += " immutable";
			if( fieldOptions.classes ) {
				elementClasses += " " + fieldOptions.classes;
			}
			
			var immutableElement = '<div>' + elementValue + '</div>';
			immutableElement = element.before(immutableElement).prev();
			immutableElement.addClass(elementClasses);
			var elementId = element.attr('id');
			if( elementId ) {
				immutableElement.attr('id', elementId + "-immutable")
			}
			
			if( $.isFunction(fieldOptions.createCallback) ) {
				fieldOptions.createCallback(immutableElement);
			}
			
			immutableElement.hide();
			self.options.immutables.push(immutableElement[0]);
			self._linkEditableToImmutable(element, immutableElement, fieldOptions.formatter);
		});
		
		// Take the checkbox away from the "all elements" list
		// checkboxes are already pushed to checkboxes array
		this.options.elements = this.options.elements.not(".checkbox-as-disabled");
		
		// Toggle the value before calling toggle so that 
		// the state is toggled back to current isEditable value
		// toggleElement takes care of all the visibility handling
		// so it is easier to do it this way
		this.options.isEditable = !this.options.isEditable;
		this.toggleElements();
		this._initEditLinks();
	},
	/**
	 * Toggles the visibility of the editable elements
	 */
	toggleElements: function() {
		if( this.options.isEditable === false ) {
			this.showEditables();
		} else {
			// TODO: Update values to immutables
			// TODO: Could the div values be used as reset feature?
			this.updateFields();
			this.hideEditables();
		}
		
	},
	/**
	 * Hides editable elements. Shows uneditable elements.
	 */
	hideEditables: function() {
		this.options.elements.hide();
		this.options.hideableElements.hide();
		$(this.options.checkboxes).attr('disabled','disabled');
		$(this.options.immutables).show();
		this.options.isEditable = false;
	},
	/**
	 * Shows editable elements. Hides uneditable elements.
	 */
	showEditables: function() {
		this.options.elements.show();
		this.options.hideableElements.show();
		$(this.options.checkboxes).removeAttr('disabled');
		$(this.options.immutables).hide();
		this.options.isEditable = true;
	},
	updateFields: function() {
	    $(this.options.checkboxes).trigger("change");
		this.options.elements.trigger("change");
	},
	hideLink: function() {
		if( this.options.linkElement ) {
			this.options.linkElement.hide();
		}
	},
	showLink: function() {
		if( this.options.linkElement ) {
			this.options.linkElement.show();
		}
	},
	
	
	// Private
	
	/**
	 * 
	 * @param {Object} fieldOptions Object containing options for a single field
	 * @param {Object} globalOptions Global options
	 * @param {String} option Name of the option
	 * @returns {Boolean} True if field option is true or global option is true. Field option overrides global option.
	 */
	_isOptionTrue: function(fieldOptions, globalOptions, option) {
		var fieldOption = fieldOptions[option];
		var globalOption = globalOptions[option];
		return (fieldOption === true || 
		(fieldOption === undefined && globalOption === true));
	},
	/**
	 * Finds input and select elements
	 * @param {String} fields: String or jQuery object list
	 * @returns jQuery object array containing input and select elements
	 */
	_findElements: function(fields, ignores) {
		// If the fields attribute contains jQuery selector
		// evaluate that first
		if( typeof fields === "string" ) {
			fields = $(fields);
		}
		if( typeof ignores === "string" ) {
		    ignores = $(ignores);
		}
		
		// In case the user gave us div or fieldset, select
		// the select and input elements, otherwise the user
		// should've given us list of input and select elements
		if( fields.is('div') || fields.is('fieldset') ) {
			return $("input, select, textarea", fields).not(ignores);
		} else {
			return $(fields).not(ignores);
		}
	},
	_findHideableElements: function(fields, additionalElements) {
	    // If the fields attribute contains jQuery selector
		// evaluate that first
		if( typeof fields === "string" ) {
			fields = $(fields);
		}

		// In case the user gave us div or fieldset, select
		// the select and input elements, otherwise the user
		// should've given us list of input and select elements
		if( fields.is('div') || fields.is('fieldset') ) {
			fields = $("button, submit, img", fields);
		} else {
			fields = $(fields);
		}
		if( additionalElements != null ) {
		    return $().merge(fields, additionalElements);
		} else {
		    return fields;
		}

	},
	/**
	 * Tries to find field options by id and name (in that order).
	 * @param fieldName Field name attribute
	 * @param fieldId Field id attribute
	 * @returns {Object} Returns field option object or empty object if field option object is not found for the field.
	 */
	_findFieldOptions: function(fieldName, fieldId) {
		var fieldOptionObject = this.options.fieldOptions[fieldId] || this.options.fieldOptions[fieldName];
		return fieldOptionObject || {};
		
	},
	/**
	 * Connects editable elements change event to change immutable field value
	 * @param editableElement
	 * @param immutableElement
	 * @param {Function} formatter Optional formatter
	 */
	_linkEditableToImmutable: function(editableElement, immutableElement, formatter) {
		var self = this;
		editableElement.change(function(event) {
			self._updateImmutableData(editableElement, immutableElement, formatter);
		});
	},
	/**
	 * Updates the displayed data of the given editable field.
	 * @param editableElement
	 * @param immutableElement
	 * @param {Function} formatter Optional formatter for data
	 */
	_updateImmutableData: function(editableElement, immutableElement, formatter) {
		var elementValue = this._getValueFromElement(editableElement);
		if( $.isFunction(formatter) ) {
			elementValue = formatter(elementValue);
		}
		this._setImmutableValue(immutableElement, editableElement, elementValue);
	},
	_setImmutableValue: function(immutable, element, elementValue) {
		if( elementValue === null || elementValue === undefined || elementValue.length === 0 ) {
		    var fieldNameOptions = this._findFieldOptions(element.attr('id'), element.attr('name'));
			var fieldClassOptions = this._findClassOptions(this,element);
			var fieldOptions = $().extend(true,{},fieldNameOptions,fieldClassOptions);
			if( this._isOptionTrue(fieldOptions, this.options, "markEmptyWithDash") ) {
				elementValue = "-";
			} else {
				elementValue = "";
			}
		}
		immutable.text(elementValue);
	},
	/**
	 * Returns the value that represents the field data.
	 * @param element Field element
	 * @returns Value as string
	 */
	_getValueFromElement: function(element) {
	    if( element.is("input:checkbox") ) {
	        return element.is(":checked") ? true : false;
	    } else if( element.is("input") || element.is("textarea") ) {
			return element.val();
		} else if( element.is("select") ) {
			return $(":selected", element).text();
		} else {
			throw "Unsupported element type";
		}
	},

	_initEditLinks: function() {
	    var self = this;
	    // Ensure that the link is jQuery object and
		// create event link for toggling the state
		if( typeof this.options.linkElement === "string" ) {
			this.options.linkElement = $(this.options.linkElement);
		}
		if( typeof this.options.uneditLinkElement === "string" ) {
			this.options.uneditLinkElement = $(this.options.uneditLinkElement);
			// Force this true so that links are toggled
			this.options.hideLinkAfterClick = true;
		}
		if( this.options.uneditLinkElement !== null ) {
		    if( this.options.isEditable ) {
		        this.options.linkElement.hide();
		        this.options.uneditLinkElement.show();
		    } else {
		        this.options.uneditLinkElement.hide();
		        this.options.linkElement.show()
		    }
		}
		this.options.linkElement.click(function() {
			self.toggleElements();
			if( self.options.hideLinkAfterClick === true ) {
				self.options.linkElement.hide();
			}
			// Show after hide so that if the element is same
			// it will be reshown if unedit link is defined
			if( self.options.uneditLinkElement !== null ) {
			    self.options.uneditLinkElement.show();
			}
			return false;
		});
		if( this.options.uneditLinkElement !== null ) {
            this.options.uneditLinkElement.unbind('click');
            this.options.uneditLinkElement.click(function() {
                self.toggleElements();
                if( self.options.hideLinkAfterClick === true ) {
                    self.options.uneditLinkElement.hide();
                }
                self.options.linkElement.show();
                return false;
            });
		}
	},
	_pickClassOptions: function(self) {
	    for(var i in self.options.fieldOptions) {
	        if( i.indexOf(self.options.fieldOptionClassPrefix) === 0 ) {
                var option = self.options.fieldOptions[i];
                self.classOptions[i.substring(self.options.fieldOptionClassPrefix.length)] = option;
	        }
	    }
	},
	_findClassOptions: function(self,element) {
	    for( var i in self.classOptions ) {
	        if( element.hasClass(i) ) {
	            return self.classOptions[i];
	        }
	    }
	    return {};
	}
});
