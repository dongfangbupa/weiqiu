<%inherit file="layout.mako"/>
<%block name="body">
    <div class="content-right">
        <ul>
            <li>
                <label>Purpose</label>
                <select>
                    <option>Advertiser</option>
                    <option>Partnership</option>
                    <option>Investment</option>
                    <option>General contact</option>
                </select>
            </li>
            <li>
                <label>Your Email</label>
                <input/>
            </li>
        </ul>
        <textarea>Plain Text</textarea>
    </div>
</%block>