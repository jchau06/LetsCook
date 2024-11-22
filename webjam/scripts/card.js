class Card {
    // Card class to create a recipe card
    constructor(title, cookTime, imageUrl, linkUrl) {
        // define basic properties of a card
        this.title = title;
        this.imageUrl = imageUrl;
        this.linkUrl = linkUrl;
        this.cookTime = cookTime
        this.maxLength = 15;
    }

    truncateStr(str, maxLength) {
        // Truncate the string if it is too long.
        if (str.length > maxLength) {
            return str.slice(0, maxLength) + "...";
        } else {
            return str;
        }
    }

    calculateCookTime() {
        // Calculate the time to cook a recipe in hours, or minutes if <60 minutes.
        if (this.cookTime < 60) {
            return String(this.cookTime) + ' min.'; 
        }

        var hrs = Math.round((this.cookTime/60)*2)/2;

        if (hrs > 12) {
            return "12+ hrs";
        }
        if (hrs === 1) {
            return "1 hr";
        }

        return String(hrs) + " hrs.";
    }

    render() {
        // creates the html for the card.
        const cardElement = document.createElement('div');
        cardElement.className = 'card';

        // image on the top left of the card.
        const imageElement = document.createElement('img');
        imageElement.src = this.imageUrl;
        imageElement.alt = "Recipe CARD:" + this.title;

        // text on the bottom right of the card.
        const titleElement = document.createElement('card-text');
        titleElement.textContent = this.truncateStr(this.title, this.maxLength);

        const timeElement = document.createElement('cook-time-text');
        timeElement.textContent = this.calculateCookTime();
        // links the card to the recipe page, sepecified as a parameter.
        const linkElement = document.createElement('a');
        linkElement.href = this.linkUrl;

        // set the hierarchy of the elements.
        linkElement.appendChild(imageElement);
        linkElement.appendChild(titleElement);
        linkElement.appendChild(timeElement);

        // add element to the full card element.
        cardElement.appendChild(linkElement);

        return cardElement;
    }
}
