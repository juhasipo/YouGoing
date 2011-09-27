/**
 *   Section Manager widget - Version 0.2
 * Creates new section selection widget which enables user to choose a section
 * via select box. User can also create new sections via link and choose a type
 * for the new section.
 * 
 *  Usage:
 * Create an element (e.g. div) with ID which contains all the following elements 
 * (class names can be overriden via options):
 *  header: E.g. div with class "section-header" and contains a select box input with class "section-selectbox"
 *  sections: 0..n number of sections with class "section"
 *  section template: A template section which will be hidden. Surrounding element of templates should have
 *                    class "section-template". See <b>"Element name and ID"</b> for more information.
 *  section footer: Element with class "section-add" containing a link with class "section-add". Optional select box
 *                  for selecting new section type. Implement the callback selectSectionType to get the section type
 *                  when the link is clicked.
 *  
 *  Sections and section templates may have input fields for section type and ID selected via sectionTypeElement and 
 *  sectionIdElement. As the names suggest these input fields will contain section type (returned by selectSectionType
 *  callback) and section ID.
 *  
 *  Section Element Name and ID:
 * Sections should have input elements named by using the index of that section. E.g. "customer.address[0].name"
 * would be the customer.address.name property of the first address section.
 * 
 * Section templates should have input elements named by using placeholder "{i}". This place holder
 * is replaced with the index of the section. E.g. second section could have input with name 
 * "customer.address[{i}].name". This input name would be replaced with "customer.address[1].name. 
 * Same placeholder replacement will be done for input's id attribute and the for attribute of the
 * corresponding label fields.
 * 
 *  Temporary Section ID:
 * When a new section is created and the section has an sectionId input, the section ID will be a negative integer.
 * The integer will start from -1 and will decrease each time a new section is created. This temporary ID can be used
 * to link different Section Manager sections when processing data on client and on server.
 * 
 *  Removed Sections:
 * TODO
 * 
 *  Note:
 * Surrounding div MUST have an ID.
 * 
 *     Options:
 *  Callbacks:
 * sectionChange: Called when section has been changed
 * 					function(baseElement, select, section)
 * addSection: Called when a section is added (also when initializing)
 * 					function(section, initializing, option)
 * formatHeader: Called to get formatted header for a new section. Default formatter will return empty header.
 * 					function(type) : return <formatted header as string>
 * selectBoxes: Should return jQuery object list of select boxes to which the new sections should be added.
 * selectSectionType: Called when the selected type for section creation is needed. Should return the type as
 *                    a string, undefined if the selection is invalid (e.g. selection "Select address type") or
 *                    null if the type isn't used.
 * cloneTemplate: Method used to create a clone of the template.
 *                  function(type, baseElement) : return <clone of the template>
 * singleValues: Array of string containing the value attributes for options which should be removed
 *               when the new section is created. The user has to prepare the select so that doesn't have
 *               any of those values when adding values to the select box.
 *               
 *  Properties:
 * hideUnselected: Set to true if only selected section should be visible. False if all section should be
 *                 shown all times. False also hides the header containing section selection box. (default: true)
 * useSectionTypeSelection: Set to false if you don't want to use select box for selecting new section type. (default: true)
 *                 
 *  Classes:
 * headerElementClass: Class of the header section containing section selection box. (default: "section-header")
 * sectionSelectElementClass: Select box used to select the visible section(default: "section-selectbox")
 * sectionClass: Section class (default: "section")
 * templateSectionClass: Section template class (default: "section-template")
 * addSectionElementClass: Class of section containing "add new" link and type for new section. (default: "section-add")
 * newLinkClass: Class for "add new" link. Has to be inside section marked with class <i>addSectionElementClass</i> (default: "section-add")
 * sectionHeaderClass: Class for section header containing select with class <i>sectionSelectElementClass</i> (default: "section-header-text")
 * sectionTypeElement: Input field in which section type is stored. (optional) (default: "input.section-type")
 * sectionIdElement: Input field in which section id is stored. (optional) (default: "input.section-id")
 * 
 * Depends:
 *   jquery.ui.core.js
 *   jquery.ui.widget.js
 */
$.widget("ui.sectionManager", {
	// Default values for jQuery UI widget
	options: {
		// Callbacks
		sectionChange: undefined,
		addSection: undefined,
		formatHeader: undefined,
		selectBoxes: undefined,
		selectSectionType: undefined,
		cloneTemplate: undefined,
		
		singleValues: [],
		
		// Toggleable features
		hideUnselected: true,
		useSectionTypeSelection: true,
		
		// Classes
		headerElementClass: "section-header",
		sectionSelectElementClass: "section-selectbox",
		sectionClass: "section",
		templateSectionClass: "section-template",
		addSectionElementClass: "section-add",
		newLinkClass: "section-add",
		removeLinkClass: "section-remove",
		sectionHeaderClass: "section-header-text",
		sectionTypeElement: "input.section-type",
		sectionTypeSelectClass: "section-type-select",
		sectionIdElement: "section-id",
		sectionSelectedClass: "section-selected"
	},
	
	// Public methods
	
	hideUnselected: function() {
		this.options.hideUnselected = true;
		this._updateSectionVisibility();
	},
	showUnselected: function() {
		this.options.hideUnselected = false;
		this._updateSectionVisibility();
	},
	
	removeSection: function(sectionId) {
		// TODO
	},
	
	// Member variables
	baseId: null,
	baseElement: null,
	sectionTempId: -1, // Temp ID to use until the entity has a real ID
	sectionsCount: 0,
	sections: [],
	templateElement: null,
	headerElement: null,
	sectionSelect: null,

	
	// Default handlers
	
	/**
	 * Default handler for new section type selection
	 * @param baseElement
	 * @returns Returns value of the selected option
	 */
	_selectNewSectionType: function(baseElement) {
		if( this.useSectionTypeSelection === false ) {
			return null;
		}
		var selected = $("." + this.sectionTypeSelectClass + " > option:selected", baseElement);
		var value = selected.val();
		if( value === "" ) {
			return undefined;
		} else {
			return value;
		}
	},
	/**
	 * Returns dummy header. User should implement of method for this and use
	 * options.formatHeader
	 * @param type Section type
	 * @returns {String} Empty string.
	 */
	_defaultHeaderFormatter: function(type) {
		return "";
	},
	/**
	 * Removes selected type from new section type select box
	 * @param type
	 * @param baseElement
	 */
	_removeSelectedType: function(type, baseElement) {
		$("." + this.sectionSelectElementClass + ' > option[value="'+type+'"]', baseElement).remove();
	},
	/**
	 * Clones the correct template and returns it to caller.
	 * @param newType New section type
	 * @param baseElement Base element
	 * @returns Cloned template
	 */
	_getClonedTemplate: function(newType, baseElement) {
		return $("." + this.templateSectionClass, baseElement).first().clone(true, true);
	},
	
	// Private implementation
	

	
	_create: function() {
		var self = this;
		this.baseElement = this.element;
		this.baseId = this.baseElement.attr("id");
		Util.assert(typeof this.baseId === "string" && this.baseId.length > 0, "No baseId");
		this.headerElement = $("." + self.options.headerElementClass, this.baseElement).first();
		Util.assert(this.headerElement.length > 0, "No header element found");
		this.sectionSelect = $("." + self.options.sectionSelectElementClass, this.headerElement);
		Util.assert(self.sectionSelect.length > 0, "No select element found");
		this.sections = $("." + self.options.sectionClass, this.baseElement);
		this.sectionsCount = this.sections.length;
		this.templateElement = $("." + self.options.templateSectionClass, this.baseElement);
		
		this._initSectionVisibility();
		this._triggerInitCallback();
		
		this._setDefaultFunction("formatHeader", this._defaultHeaderFormatter);
		this._setDefaultFunction("selectSectionType", this._selectNewSectionType);
		this._setDefaultFunction("cloneTemplate", this._getClonedTemplate);

		
		var newLink = $("." + self.options.addSectionElementClass + " a." + self.options.newLinkClass, this.baseElement);
		newLink.click(function() { return self._createAndInitNewSection(self); }); // new link
		
		
		var selectChanged = function(event) {
			if( self.options.hideUnselected ) {
				self._updateSectionVisibility();
			}
		};
		
		self.sectionSelect.change(selectChanged);
		self.sectionSelect.keyup(selectChanged);
	},
	
	/**
	 * Creates a new section and sets visibility of all sections.
	 * Adds options to correct select boxes. Updates counters.
	 * 
	 * @param {this} self Widget itself
	 * @returns {Boolean} Always false in order to work with jQuery click handlers.
	 */
	_createAndInitNewSection: function(self) {
		// Generate new section from a template
		var newType = self.options.selectSectionType(self.baseElement);
		if( newType === undefined ) {
			return false;
		}
		var headerText = self.options.formatHeader(newType);
		var newSection = self._createNewSection(newType, headerText, self.baseId); 
		
		// Replace placeholder indeces of input fields
		// Name obligatory, id optional for inputs
		$("input, select, textarea", newSection).each(function() {
			var input = $(this);
			var inputName = input.attr('name');
			var sectionCountStr = self.sectionsCount.toString();
			var inputId = input.attr('id');
			
			input.attr('name', inputName.replace("\{i\}", sectionCountStr));
			if( inputId ) {
				var label = $('label[for="'+inputId+'"]', newSection);
				inputId = inputId.replace("\{i\}", sectionCountStr);
				input.attr('id', inputId);
				label.attr('for', inputId);
			}
		});
		
		// Update sections variable
		self.sections = $("." + self.options.sectionClass, self.baseElement);
		Util.assert(self.sections.length > 0, "No sections found");
		Util.assert(self.sections.length === (self.sectionsCount + 1), "Too few sections after adding one");
		if( self.options.hideUnselected ) {
			self.sections.hide();
		}
		newSection.show();
		
		
		// Replace ID with temporary ID
		// Temp ID will be used to connect contact entities
		// on server side
		$(self.options.sectionIdElement, newSection).val(self.sectionTempId);
		
		// Add new value to select box (and other select boxes if specified)
		var optionEl = '<option value="'+self.sectionsCount+'">'+headerText+'</option>';
		var optionEl2 = '<option value="'+self.sectionTempId+'">'+headerText+'</option>';
		self.sectionSelect.append(optionEl);
		if( $.isFunction(self.options.selectBoxes) ) {
			var additionalSelectBoxes = self.options.selectBoxes();
		} else {
			var additionalSelectBoxes = $(self.selectBoxes);
		}
		additionalSelectBoxes.each(function() {
			$(this).append(optionEl2);
		});
		self.sectionSelect.val(self.sectionsCount);
		
		++self.sectionsCount;
		--self.sectionTempId;
		
		if( $.isFunction(self.options.addSection) ) {
			self.options.addSection(newSection, false, $("option[value='"+(self.sectionsCount-1)+"']", self.sectionSelect));
		}
		if( $.isFunction(self.options.sectionChange) ) {
			self.options.sectionChange(self.baseElement, self.sectionSelect, newSection);
		}
		
		return false;
	},
	
	/**
	 * Initializes element visibility
	 */
	_initSectionVisibility: function() {
		this.templateElement.hide();
		if( this.options.hideUnselected === true ) {
			this.sections.hide();
			// Only show section if there is at least one section in addition
			// template section
			this.sections.first().show();
		} else {
			this.headerElement.hide();
		}
	},
	/**
	 * Triggers callbacks used in initialization phase
	 */
	_triggerInitCallback: function() {
		// trigger add
		var self = this;
		this.sections.each(function() {
			if($.isFunction(self.options.addSection) ) {
				self.options.addSection($(this), true);
			}
		});
		
		if( $.isFunction(self.options.sectionChange)) {
			self.options.sectionChange(self.options.baseElement, this.sectionSelect, this.sections.first());
		}
	},
	/**
	 * Removes a type value from type selection select box
	 * @param {String} newType Type to remove
	 */
	_removeSingleValues: function(newType) {
		if( newType ) {
			// If only single value for the type is allowed, remove the value from the list
			for( var i in this.options.singleValues ) {
				if( newType === this.options.singleValues[i] ) {
					this._removeSelectedType(newType);
					break;
				}
			}
		}
	},
	/**
	 * Creates new section and removes type option from type selection select box if necessary.
	 * @param {String} newType Type of the new section as string
	 * @param {String} headerText Header text as string
	 * @param {String} baseId Base ID to use as new section's id prefix
	 * @returns New section
	 */
	_createNewSection: function(newType, headerText, baseId) {
		// Called via "self" => this points to widget (and not 
		// to options object
		var newSection = this.options.cloneTemplate(newType, this.baseElement);
		var newSectionId = baseId + "-" + this.sectionsCount;
		newSection.attr('id', baseId + "-" + this.sectionsCount);
		newSection.removeClass(this.options.sectionTemplateClass);
		newSection.addClass(this.options.sectionClass);
		
		// Wrap the section in div to get the "outer HTML"
		// and add that "outer HTML" as the last element of real addresses
		newSection = newSection.wrapAll("<div>").parent();
		var placeToAdd = this.sections.last();
		if (placeToAdd.length == 0) {
			placeToAdd = this.templateElement;
			Util.assert(placeToAdd.length > 0, "No place found where to add the new section");
		}
		placeToAdd.after(newSection.html());			
		newSection = $("#" + newSectionId);
		
		// Set type and header for the new section
		this._removeSingleValues(newType);
		
		// Replace header
		$("." + this.options.sectionHeaderClass, newSection).text(headerText);
		if( newType ) {
			$(this.options.sectionTypeElement, newSection).val(newType);
		}
		return newSection;
	},
	/**
	 * Sets default value for callback function of the given name
	 * if the callback function isn't set via options by the user
	 * @param {String} name Name of the function
	 * @param {Function} defaultFunction Default function to use
	 */
	_setDefaultFunction: function(name, defaultFunction) {
		if( !$.isFunction(this.options[name]) ) {
			this.options[name] = defaultFunction;
		}
	},
	
	/**
	 * Updates section visibility using options.hideUnselected value
	 * Triggers sectionChange when options.hideUnselected is true. Also hides/shows header section.
	 */
	_updateSectionVisibility: function() {
		if( this.options.hideUnselected === true ) {
			this.sections.hide();
			this._getSelectedSection().show();
			this.headerElement.show();
			if( $.isFunction(this.options.sectionChange) ) {
				this.options.sectionChange(this.baseElement, this.sectionSelect, this._getSelectedSection());
			}
		} else {
			this.sections.show();
			this.headerElement.hide();
		}
	},
	/**
	 * Returns the selected section. Gets the selection state from the header section select box.
	 * Return value is only valid when the options.hideUnselected is true
	 * @returns Selected section
	 */
	_getSelectedSection: function() {
		var id = this.sectionSelect.val();
		var newSection = $("#" + this.baseId + "-" + id);
		return newSection;
	}
	
	
});