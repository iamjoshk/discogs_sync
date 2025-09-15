> [!IMPORTANT]
> This custom integration is still in early development phase. Existing features are working, though they may be updated or changed in the future.


# Discogs Sync - Home Assistant Discogs Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/iamjoshk/discogs_sync)](https://github.com/iamjoshk/discogs_sync/releases)

This integration brings your full [Discogs](https://www.discogs.com) collection into Home Assistant, expanding on the legacy core Discogs integration. It provides sensors for collection size, wantlist size, collection value, random record with configurable folder, folders list, and user lists. It also includes actions that can fetch your entire collection, wantlist, or user lists and make them available for display using cards like flex-table-card or downloaded as a JSON file.

## Features

- Collection count sensor
- Wantlist count sensor
- Collection value sensors (minimum, median, maximum)
- Random record sensor with details and artwork
- Configurable folder selection for the random record
- User lists sensor with list details in attributes
- User folders sensor with folder details in attributes
- Buttons to refresh data for each API endpoint
- Actions that return collection, wantlist, and user lists data for use in dashboards
- Rate limit monitor
- Support for flex-table-card integration

## Installation

### HACS Installation (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=iamjoshk&repository=https%3A%2F%2Fgithub.com%2Fiamjoshk%2Fdiscogs_sync&category=integration)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS:
   - Go to HACS in Home Assistant
   - Click the three dots in the upper right corner
   - Select "Custom repositories"
   - Add `https://github.com/iamjoshk/discogs_sync` with category "Integration"
3. Click "Add"
4. Then download the add-on
5. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/iamjoshk/discogs_sync/releases)
2. Unpack the release and copy the `custom_components/discogs_sync` directory into your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Integration Setup

1. In Home Assistant, go to **Settings** > **Integrations**
2. Click the **+ ADD INTEGRATION** button
3. Search for "Discogs Sync" and select it
4. Enter your Discogs API token
   - You can get your token from your [Discogs Developer Settings](https://www.discogs.com/settings/developers)
5. Click "Submit"

### API Token

To get your Discogs API token:

1. Log in to your Discogs account
2. Go to [Settings > Developers](https://www.discogs.com/settings/developers)
3. Generate a personal access token
4. Copy the token and use it during integration setup

### Integration Settings

During integration set up, and later using the settings gear in the integration, you can set the update interval individually for the collection, waitlist, random record, collection values, folders, and lists entities. These intervals are in minutes. If you disable the automatic updates, then you can use automations to press the refresh buttons and refresh data from each endpoint at any interval you decide. You can also always press the buttons for an on-demand update even with automatic updates enabled.

## Entities Created

+ Collection sensor: A sensor that counts the number of releases in your collection folder.
+ Collection Value sensors: 3 sensors that report the minimum, median, and maximum value of your collection based on Discogs sales.
+ Wantlist sensor: A sensor that counts the number of releases in your wantlist.
+ User Lists sensor: A sensor that counts the number of lists in your account. Attributes include name, id, uri, and public status for each list.
+ User Folders sensor: A sensor that counts the number of collection folders in your account. Attributes include id, count, name, and resource_url for each folder.
+ Random Record sensor: A sensor that displays a random record from your collection with details and artwork.
+ Random Record Folder input select: a dropdown that lets you choose which folder to use for your random record sensor
+ Rate Limit binary sensor: Turns on if the Discogs API rate limit has been hit. Attributes include the number of calls in the last minute.
+ Refresh buttons: Individual buttons to manually refresh data for each endpoint (collection, wantlist, collection value, random record, user lists, and user folders).

## Available Actions

Note: the data returned even for small collections will exceed the system limit (65535 characters) for entity attributes, so the download collection, wantlist, and user list action responses are returned as responses only with an option to download the response as a JSON file. The responses will NOT be saved to an entity.


The response can be used as a variable in a script or automation.

### Download Collection Action - discogs_sync.download_collection

This action fetches your complete Discogs collection and can optionally save it to a JSON file.

Parameters:
- `path` (optional): Path to save the collection file (default: `discogs_collection.json` in config folder)
- `download` (optional): Whether to save to file (default: `false`)
- `folder_id` (optional): Specify the folder id to download releases from (default: `0` which is the Discogs-created `All` folder)

Returns:
- Your complete collection data from the `All` folder (or specific folder if defined in the parameters)

Example response: 
```
collection:
  - id: 8302412
    master_id: 72316
    master_url: https://api.discogs.com/masters/72316
    resource_url: https://api.discogs.com/releases/8302412
    thumb: >-
      https://i.discogs.com/7C6ONIvFG8eJ4oMjVyk81DyWdsvsTxTcJh9I3ocFBDU/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTgzMDI0/MTItMTQ1ODk0OTc4/OS0zNDg2LmpwZWc.jpeg
    cover_image: >-
      https://i.discogs.com/Xx4FZdNgsitGd1sqGnH3WokFfd2ZS67jok7ylJ5f4Ks/rs:fit/g:sm/q:90/h:598/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTgzMDI0/MTItMTQ1ODk0OTc4/OS0zNDg2LmpwZWc.jpeg
    title: The Best Of Procol Harum
    year: 0
    formats:
      - name: Vinyl
        qty: "1"
        text: CRC
        descriptions:
          - LP
          - Compilation
          - Club Edition
          - Stereo
    labels:
      - name: A&M Records
        catno: SP-3259
        entity_type: "1"
        entity_type_name: Label
        id: 904
        resource_url: https://api.discogs.com/labels/904
    artists:
      - name: Procol Harum
        anv: ""
        join: ""
        role: ""
        tracks: ""
        id: 254414
        resource_url: https://api.discogs.com/artists/254414
    genres:
      - Rock
    styles: []
  - id: 3036891
    master_id: 24047
    master_url: https://api.discogs.com/masters/24047
    resource_url: https://api.discogs.com/releases/3036891
    thumb: >-
      https://i.discogs.com/FaF4s-fa_TWaWaldWbx-VUdc5sju2XU-NBBVgfc2qsg/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTMwMzY4/OTEtMTMxMjc3ODcz/Mi5qcGVn.jpeg
    cover_image: >-
      https://i.discogs.com/3ES45b8C7QNHx9Eg5P3aGthgz0P0YBlmpFXwuQvkiuw/rs:fit/g:sm/q:90/h:500/w:500/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTMwMzY4/OTEtMTMxMjc3ODcz/Mi5qcGVn.jpeg
    title: Abbey Road
    year: 1971
    formats:
      - name: Vinyl
        qty: "1"
        text: Winchester Pressing
        descriptions:
          - LP
          - Album
          - Reissue
          - Stereo
    labels:
      - name: Apple Records
        catno: SO-383
        entity_type: "1"
        entity_type_name: Label
        id: 25693
        resource_url: https://api.discogs.com/labels/25693
    artists:
      - name: The Beatles
        anv: ""
        join: ""
        role: ""
        tracks: ""
        id: 82730
        resource_url: https://api.discogs.com/artists/82730
    genres:
      - Rock
    styles:
      - Pop Rock
  - id: 1485752
    master_id: 56036
    master_url: https://api.discogs.com/masters/56036
    resource_url: https://api.discogs.com/releases/1485752
    thumb: >-
      https://i.discogs.com/l35SMx1IwmvVzGn2_xXSXxTxAgL8T-Dvmpchxh-K0YQ/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTE0ODU3/NTItMTU5MDM2NDk4/OS04NDEyLmpwZWc.jpeg
    cover_image: >-
      https://i.discogs.com/C1kPzw91t--voE29LbYSgDzMd5QaT-f_qnPAtRCpG9I/rs:fit/g:sm/q:90/h:600/w:598/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTE0ODU3/NTItMTU5MDM2NDk4/OS04NDEyLmpwZWc.jpeg
    title: All Things Must Pass
    year: 1970
    formats:
      - name: Vinyl
        qty: "3"
        text: "Winchester Pressing "
        descriptions:
          - LP
          - Album
          - Stereo
      - name: Box Set
        qty: "1"
        descriptions: []
    labels:
      - name: Apple Records
        catno: STCH 639
        entity_type: "1"
        entity_type_name: Label
        id: 25693
        resource_url: https://api.discogs.com/labels/25693
    artists:
      - name: George Harrison
        anv: ""
        join: ""
        role: ""
        tracks: ""
        id: 243955
        resource_url: https://api.discogs.com/artists/243955
    genres:
      - Rock
    styles:
      - Pop Rock
  - id: 12775821
    master_id: 46402
    master_url: https://api.discogs.com/masters/46402
    resource_url: https://api.discogs.com/releases/12775821
    thumb: >-
      https://i.discogs.com/84NuSy4HCVkrkqj83kot90h48K2ZUrbey0Q34tYADN0/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEyNzc1/ODIxLTE1NDIxODIw/MTQtMTg0Ni5qcGVn.jpeg
    cover_image: >-
      https://i.discogs.com/8FDLemdNLoUnj8jBGiEZGYaG0kVB1LUBGPZZcbxOLHI/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTEyNzc1/ODIxLTE1NDIxODIw/MTQtMTg0Ni5qcGVn.jpeg
    title: The Beatles And Esher Demos
    year: 2018
    formats:
      - name: Vinyl
        qty: "2"
        text: 180g
        descriptions:
          - LP
          - Album
          - Reissue
          - Remastered
          - Stereo
      - name: Vinyl
        qty: "2"
        text: 180g
        descriptions:
          - LP
          - Stereo
      - name: Box Set
        qty: "1"
        descriptions:
          - Compilation
    labels:
      - name: Apple Records
        catno: "0602567572015"
        entity_type: "1"
        entity_type_name: Label
        id: 25693
        resource_url: https://api.discogs.com/labels/25693
      - name: Universal Music Group International
        catno: "0602567572015"
        entity_type: "1"
        entity_type_name: Label
        id: 138199
        resource_url: https://api.discogs.com/labels/138199
    artists:
      - name: The Beatles
        anv: ""
        join: ""
        role: ""
        tracks: ""
        id: 82730
        resource_url: https://api.discogs.com/artists/82730
    genres:
      - Rock
      - Pop
    styles:
      - Rock & Roll
      - Pop Rock
      - Soft Rock
      - Psychedelic Rock
      - Experimental
      - Country Rock
      - Blues Rock
      - Avantgarde
```

### Download Wantlist Action - discogs_sync.download_wantlist

This action fetches your complete Discogs wantlist and can optionally save it to a JSON file.

Parameters:
- `path` (optional): Path to save the collection file (default: `discogs_wantlist.json` in config folder)
- `download` (optional): Whether to save to file (default: `false`)

Returns:
- Your complete wantlist data

Example response:
```
wantlist:
  - id: 31381
    master_id: 19493
    master_url: https://api.discogs.com/masters/19493
    resource_url: https://api.discogs.com/releases/31381
    title: Head Hunters
    year: 1973
    formats:
      - name: Vinyl
        qty: "1"
        descriptions:
          - LP
          - Album
        text: Pitman Pressing
    artists:
      - name: Herbie Hancock
        anv: ""
        join: ""
        role: ""
        tracks: ""
        id: 3865
        resource_url: https://api.discogs.com/artists/3865
    labels:
      - name: Columbia
        catno: KC 32731
        entity_type: "1"
        entity_type_name: Label
        id: 1866
        resource_url: https://api.discogs.com/labels/1866
    thumb: >-
      https://i.discogs.com/hNhSZVdUZjUKO3ST78dt9TQ-muc62zOH9CWVk7z4WYk/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTMxMzgx/LTE0MzMyNTkxNDMt/ODUyMi5qcGVn.jpeg
    cover_image: >-
      https://i.discogs.com/PzhEnDeEy-u3foEvF-q1mPZDeTGt__d6k4j9XUZ7q_c/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTMxMzgx/LTE0MzMyNTkxNDMt/ODUyMi5qcGVn.jpeg
    genres:
      - Jazz
    styles:
      - Jazz-Funk
  - id: 677581
    master_id: 72232
    master_url: https://api.discogs.com/masters/72232
    resource_url: https://api.discogs.com/releases/677581
    title: Janis Joplin's Greatest Hits
    year: 1973
    formats:
      - name: Vinyl
        qty: "1"
        descriptions:
          - LP
          - Compilation
          - Stereo
        text: Pitman
    artists:
      - name: Janis Joplin
        anv: ""
        join: ""
        role: ""
        tracks: ""
        id: 120232
        resource_url: https://api.discogs.com/artists/120232
    labels:
      - name: Columbia
        catno: KC 32168
        entity_type: "1"
        entity_type_name: Label
        id: 1866
        resource_url: https://api.discogs.com/labels/1866
      - name: Columbia
        catno: KC 32168
        entity_type: "1"
        entity_type_name: Label
        id: 1866
        resource_url: https://api.discogs.com/labels/1866
    thumb: >-
      https://i.discogs.com/wBbFpOx96fY-M3ujFqje3-viUujsDAbdSre6Uutcwwg/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTY3NzU4/MS0xMjc5MzA0Njk5/LmpwZWc.jpeg
    cover_image: >-
      https://i.discogs.com/daRnbdjOFbSZjkuYZRD-W3FSoeakrgbr_KCK4rFkz0Q/rs:fit/g:sm/q:90/h:600/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTY3NzU4/MS0xMjc5MzA0Njk5/LmpwZWc.jpeg
    genres:
      - Rock
    styles:
      - Blues Rock
```

### Download User List Action - discogs_sync.download_user_list

This action fetches a specified user list and can optionally save it to a JSON file.

Parameters:
- list_id (required): list ID to download
- `path` (optional): Path to save the collection file (default: `discogs_user_list.json` in config folder)
- `download` (optional): Whether to save to file (default: `false`)

Returns:
- The complete user list data

> Note: The lists that can be queried are not limited to your lists; however, private lists are only returned when your API call is authenticated as the owner. So you can return your own private lists and any public lists as long as you know the list ID. For a public list, the list ID is the number in the URL of the list on Discogs. For example: `https://www.discogs.com/lists/Album-covers-with-cats/1593344` the list id is `1593344`. Many lists are VERY long, so it may take some time to return the response. Be careful what you do with the data!

## Using with flex-table-card

The `download_collection`, `download_wantlist`, and `download_user_list` actions can be used to populate a [flex-table-card](https://github.com/custom-cards/flex-table-card) to display your collection, wantlist, or a user list. First, install the flex-table-card from HACS.

You can run the action directly in the card OR as a script in the card. Using the action directly, you need `entities` to be empty. The advantage to using a script is auto-refreshing the card data.

### Example flex-table-card Configuration

As an action directly:
```
type: custom:flex-table-card
title: My Discogs Collection
enable_search: true
action: discogs_sync.download_collection
entities: []
sort_by:
  - Artists
  - Year
columns:
  - name: Cover
    data: collection.thumb
    modify: "x ? `<img src=\"${x}\" style=\"height:50px;\"/>` : \"\""
    align: center
  - name: Artists
    data: collection.artists
    modify: x.map(a => a.name.replace(/^The /, "")).join(", ")
  - data: collection.title
    name: Title
  - data: collection.year
    name: Year
  - name: Format
    data: collection.formats
    modify: "x && x.length > 0 ? x[0].name : \"\""
  - name: Genre
    data: collection.genres
  - name: Styles
    data: collection.styles
```

As a script:

As a script in the card, you can auto-refresh the data. Using `entity_id` in the variable lets the entity from flex-table-card be used for the script. This is an important part of the auto-refresh.

Script:
```
sequence:
  - data: {}
    response_variable: discogs
    action: discogs_sync.download_collection
  - variables:
      records: |
        {% set response = { entity_id[0]: discogs } %} {{ response }}
  - stop: All done
    response_variable: records
alias: Discogs Download Collection
```

and flex-table-card:
```
type: custom:flex-table-card
title: My Discogs Collection
enable_search: true
action: script.discogs_download_collection
entities:
  - sensor.my_collection  <-- whatever sensor you use here will be passed to the script in the entity_id.
sort_by:                      When this sensor is updated, the data will refresh.
  - Artists
  - Year
columns:
  - name: Cover
    data: collection.thumb
    modify: "x ? `<img src=\"${x}\" style=\"height:50px;\"/>` : \"\""
    align: center
  - name: Artists
    data: collection.artists
    modify: x.map(a => a.name.replace(/^The /, "")).join(", ")
  - data: collection.title
    name: Title
  - data: collection.year
    name: Year
  - name: Format
    data: collection.formats
    modify: "x && x.length > 0 ? x[0].name : \"\""
  - name: Genre
    data: collection.genres
    modify: if(x.length == 0){""}else{x}
  - name: Styles
    data: collection.styles
    modify: if(x.length == 0){""}else{x}
grid_options:
  columns: full
  rows: auto
card_mod:
  style: |
    ha-card {
      overflow: auto;
      max-height: 700px;
    }
```


Sometimes data from Discogs is incomplete or null, which causes flex-table-card to display `undefinedundefinedundefined` in the cell. You can mitigate this by using `modify: if(x.length == 0){""}else{x}` in columns.


<img width="841" height="626" alt="image" src="https://github.com/user-attachments/assets/76821464-c85d-4bd4-b3f6-f1c52627717b" />


### Markdown Card
Using a markdown card, you can create a nice looking display for the random record.

```
type: markdown
content: |-
  # **Random Play**
  ## {{ states('sensor.discogs_sync_random_record') }}
  {% set f = state_attr('sensor.discogs_sync_random_record','format') %}
  {% if 'Vinyl' in f %}
  ### Vinyl
  {% elif 'Cassette' in f %}
  ### Cassette
  {% elif 'CD' in f %}
  ### CD
  {% else %}
  ### Other
  {% endif %}
  ![image]({{ state_attr('sensor.discogs_sync_random_record','cover_image') }})
text_only: true
```

<img width="418" height="528" alt="image" src="https://github.com/user-attachments/assets/deb56a23-87f1-42fb-8547-f484953c50bb" />


## Notes

- The integration tries to respect [Discogs' API rate limits](https://www.discogs.com/developers/#page:home,header:home-rate-limiting) by adding delays between API calls (60 requests per minute for authenticated calls).
- When using the download actions with large collections or wantlists, it may take some time to complete.
- A binary sensor is created to monitor rate limit status. 
- The actions can only be called once every second to try and reduce rate limit restrictions.

## Troubleshooting

- If you see "Rate limit exceeded" warnings, wait 60 seconds before making another request
- The rate limit binary sensor will show "Problem" when rate limits are exceeded and includes information about remaining limits in the attributes.
- Editing flex-table-card calls the action repeatedly, so the data may not load until you save, wait a few seconds, and then refresh the browser.

## Credits and Inspiration

- [Discogs API Documentation](https://www.discogs.com/developers)
- [Core Discogs integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/discogs)
- [discogs-enhanced by @andreasc1](https://www.github.com/andreasc1/homeassistant-discogs-enhanced)
- [Wine-Cellar by @EdLeckert](https://github.com/EdLeckert/wine-cellar)
- [flex-table-card by @daringer](https://github.com/custom-cards/flex-table-card)
